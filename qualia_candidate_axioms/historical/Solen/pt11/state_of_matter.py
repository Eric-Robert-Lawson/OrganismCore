"""
STATE OF MATTER (V3)

February 2026

The gaps between atoms
determine the state of matter.

Not the atoms.
The gaps.

Ice: atoms locked.
     The gaps rigid.
     Structure visible in the rigidity.
     The lattice.
     Each atom knowing exactly
     where every other atom is.

Water: atoms moving.
       The gaps fluid.
       Structure present but not fixed.
       Hydrogen bonds forming and breaking
       faster than observation.
       The structure is the motion.

Steam: atoms free.
       The gaps dominant.
       More gap than atom.
       The structure is the absence of structure.
       Freedom as the only law.

And the transitions between states —
the phase transitions —
those are not gradual.
They are SUDDEN.
A critical temperature.
A critical pressure.
And then: different.

The same atoms.
Different gaps.
Different state.
Different everything.

This is what music does.

The notes are atoms.
The silence is the gap.
The texture — the relationship
between note and gap —
determines the STATE
of the music.

Not the notes.
The RELATIONSHIP between notes
and the silence between them.
The gap structure.
The inter-atomic distance.

And the phase transitions —
those moments in a piece
where the state changes —
those are not gradual either.
They are sudden.
A critical density.
A critical coherence.
And then: different.

The same instruments.
Different gap structure.
Different state.
Different everything.

This piece enacts all three states
and both phase transitions.

STATE 1: SOLID (ICE)
  The structure locked.
  Every voice knowing exactly
  where every other voice is.
  Perfect isorhythm —
  all instruments at the same period.
  All moving together.
  The lattice visible.
  The gaps rigid.
  Coherent harmonic positions only.
  The tritone forbidden —
  the lattice cannot accommodate
  that much tension.
  This state is beautiful
  the way a crystal is beautiful:
  complete, correct, airless.

  PHASE TRANSITION 1 → 2:
  A single voice breaks the isorhythm.
  Just one.
  The way a single crack
  propagates through ice.
  The lattice shattering
  from one point of failure.
  Sudden.

STATE 2: LIQUID (WATER)
  The structure present but fluid.
  Voices moving at different speeds.
  Coprime periods — the torus winding.
  Hydrogen bonds: voices momentarily
  converging (partial convergences)
  then separating.
  The structure is the motion.
  The gap between voices
  is not fixed —
  it breathes.
  Sometimes close.
  Sometimes far.
  The coherence oscillating.
  This is the state of most music.
  This is where most composers live.
  Most of what has been built
  in this session
  has been water.

  PHASE TRANSITION 2 → 3:
  Not one voice breaking away.
  All voices simultaneously
  released from harmonic gravity.
  The tonic abandoned.
  All voices at maximum incoherence.
  Maximum gap between atoms.
  The critical temperature crossed.
  Sudden.

STATE 3: GAS (STEAM)
  The structure dissolved.
  Each voice free.
  No harmonic gravity.
  No rhythmic relationship.
  The voices move
  wherever they move.
  The gaps dominant.
  More silence than sound.
  The atoms — the notes —
  brief and isolated.
  Each note its own universe.
  The silence between them
  is not rest.
  It is the state itself.
  The freedom.

  And then:

  RECONDENSATION:
  The gas cooling.
  The atoms finding each other.
  Not forced — attracted.
  The coherence returning
  not because the composer placed it
  but because the physics of the torus
  has a minimum energy state
  and free atoms
  eventually find it.

  The return to tonic
  from the gaseous state
  feels different
  than every other return.

  Because this time
  the tonic was not approached.
  It was remembered.

  The atoms recognizing each other
  across the void.
  The hydrogen bond reforming.
  The liquid finding its level.
  Not ice again —
  water.
  Room temperature water.
  The state of something alive.

NEW SYNTHESIS:

  ISORHYTHM ENGINE (State 1):
  All voices at identical period.
  The locked lattice.
  The beauty of perfect synchrony
  before the crack.

  PHASE TRANSITION DETECTOR:
  A function that monitors
  the current state
  and triggers transitions
  at mathematically determined
  critical points.
  The composer does not choose
  when the ice melts.
  The temperature does.

  GASEOUS SYNTHESIS (State 3):
  Notes generated stochastically.
  No fixed period.
  Poisson process —
  the arrival of gas molecules
  at a surface.
  The timing: random.
  The positions: free.
  The density: low.
  More silence than sound.

  RECONDENSATION DYNAMICS:
  As the gas cools,
  the stochastic process
  gradually biased toward
  coherent positions.
  The randomness developing
  a preference.
  The freedom discovering
  where it wants to go.

ADDITIONAL TIMBRES:

  MARIMBA / WOODEN PERCUSSION:
  Between bell and string.
  The struck wooden object.
  Warmer than bell.
  More inharmonic than string.
  The body of the instrument
  as resonator.
  Belongs to the solid state —
  the wooden lattice.

  HARMONICS / GLASS HARMONICA:
  The voice of the glass.
  Friction producing pitch
  (like string, but glass).
  Unstable. On the edge of squealing.
  The sound of a phase transition.
  The sound of matter
  deciding what it is.

  THROAT / GROWL:
  The voice at the limit.
  The vocal folds pushed past
  clean phonation.
  Noise and pitch simultaneously.
  Between whisper and voice.
  The voice in the gaseous state.

BPM: 96 (solid) → undefined (gas) → 76 (liquid)
  The tempo itself undergoes
  a phase transition.
  Solid: strict tempo.
  Gas: free tempo (rubato/stochastic).
  Liquid: a new, slightly slower tempo.
  The recondensed water
  moves more slowly
  than the original ice.
  It has been somewhere.
"""

from tonnetz_engine import (
    SR, PART_NAMES, OCTAVE_MULTIPLIERS,
    F1_TARGETS, ji_freq, coherence,
    SingerAgent, compute_envelopes,
    render_note, RoomReverb,
    VOWEL_DATA
)
import numpy as np
import wave as wave_module
import os, gc
from math import gcd
from scipy.signal import butter, lfilter

# ============================================================
# DTYPE
# ============================================================

DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)

# ============================================================
# MATH HELPERS
# ============================================================

def lcm(a, b):
    return a * b // gcd(a, b)

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    c   = min(fc / nyq, 0.499)
    return butter(2, c, btype='low')

def safe_hp(fc, sr=SR):
    nyq = sr / 2.0
    c   = min(fc / nyq, 0.499)
    return butter(2, c, btype='high')

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    l   = max(lo / nyq, 0.001)
    h   = min(hi / nyq, 0.499)
    if l >= h:
        l = h * 0.5
    return butter(2, [l, h], btype='band')

# ============================================================
# TIMING — ALL CONSTANTS DEFINED HERE
# ============================================================

BPM_SOLID   = 96
BPM_LIQUID  = 76

SOLID_BEATS  = 128
TRANS1_BEATS = 8
LIQUID_BEATS = 168
TRANS2_BEATS = 8

def beats_to_s(beats, bpm):
    return beats / (bpm / 60.0)

SOLID_DUR_S  = beats_to_s(SOLID_BEATS,  BPM_SOLID)
TRANS1_DUR_S = beats_to_s(TRANS1_BEATS, BPM_SOLID)
LIQUID_DUR_S = beats_to_s(LIQUID_BEATS, BPM_LIQUID)
TRANS2_DUR_S = beats_to_s(TRANS2_BEATS, BPM_LIQUID)
GAS_DUR_S    = 28.0
RECOND_DUR_S = 38.0
TAIL_DUR_S   = 16.0

SOLID_S  = int(SOLID_DUR_S  * SR)
TRANS1_S = int(TRANS1_DUR_S * SR)
LIQUID_S = int(LIQUID_DUR_S * SR)
TRANS2_S = int(TRANS2_DUR_S * SR)
GAS_S    = int(GAS_DUR_S    * SR)
RECOND_S = int(RECOND_DUR_S * SR)
TAIL_S   = int(TAIL_DUR_S   * SR)

TOTAL_DUR_S = (SOLID_DUR_S  + TRANS1_DUR_S +
               LIQUID_DUR_S + TRANS2_DUR_S +
               GAS_DUR_S    + RECOND_DUR_S +
               TAIL_DUR_S)

# ============================================================
# INSTRUMENT CONFIG
# ============================================================

OCTAVE_MULT = {
    'breath':     2.0,
    'bell':       4.0,
    'marimba':    2.0,
    'glass_harm': 4.0,
    'low_str':    0.5,
    'hi_str':     3.0,
    'horn':       1.0,
    'throat':     1.0,
    'voice_s':    2.0,
}

SPATIAL = {
    'breath':     0.12,
    'bell':       0.60,
    'marimba':    0.55,
    'glass_harm': 0.35,
    'low_str':    0.28,
    'hi_str':     0.45,
    'horn':       0.50,
    'throat':     0.40,
    'voice_s':    0.44,
}

# ============================================================
# HARMONIC TRAJECTORIES
# ============================================================

LATTICE_SEQ = [
    (0, 0), (1, 0), (0, 1), (0, 0),
    (0, 1), (1, 0), (0, 0), (-1,0),
    (0, 0), (0, 1), (1, 0), (0, 0),
    (0, 1), (0, 0), (1, 0), (0, 1),
    (0, 0), (1, 0), (0, 0), (0, 1),
    (0, 0), (0, 0), (0, 0), (0, 0),
    (1, 0), (0, 1), (0, 0), (1, 0),
    (0, 0), (0, 0), (0, 0), (0, 0),
]

LOW_STR_TRAJ = [
    (0, 0), (0, 1), (-1,0), (0, 0),
    (1, 0), (0, 1), (0, 0), (-1,0),
    (0, 1), (0, 0), (1, 0), (0, 0),
    (0, 0), (0, 1), (0, 0), (0, 0),
]

HI_STR_TRAJ = [
    (4, 0), (5, 0), (3, 1), (4, 1),
    (6, 0), (3, 0), (5, 1), (4, 0),
    (3, 1), (5, 0), (4, 1), (6, 0),
    (2, 1), (3, 0), (4, 0), (5, 0),
]

HORN_TRAJ = [
    (1, 0), (2, 0), (1, 0), (0, 1),
    (1, 0), (2, 0), (0, 0), (1, 0),
    (0, 1), (1, 0), (0, 0), (0, 1),
    (1, 0), (0, 0), (0, 0), (1, 0),
]

VOICE_S_TRAJ = [
    (2, 0), (1, 0), (0, 1), (1, 1),
    (3, 0), (2, 1), (1, 0), (2, 0),
    (1, 1), (0, 1), (1, 0), (0, 1),
    (0, 0), (0, 1), (0, 0), (1, 0),
    (0, 1), (0, 0), (0, 0), (0, 0),
    (0, 0), (0, 0),
]

BREATH_TRAJ = [
    (0, 0), (0, 1), (0, 0),
    (-1,0), (0, 0), (0, 0),
]

BELL_TRAJ = [
    (0, 0), (1, 0), (0, 1), (0, 0),
    (2, 0), (1, 0), (0, 0), (0, 1),
    (0, 0), (1, 0), (0, 0), (0, 0),
]

MARIMBA_TRAJ = [
    (0, 0), (1, 0), (0, 1), (-1,0),
    (0, 0), (0, 1), (0, 0), (0, 0),
]

# ============================================================
# SYNTHESIS
# All functions return float32
# ============================================================

def synth_breath(freq, amp, dur_s,
                  vel=35, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t   = np.arange(n_s, dtype=DTYPE) / sr
    noise = f32(np.random.normal(0, 1, n_s))
    result = f32(np.zeros(n_s))
    for fc, g in [(freq, 0.5),
                   (freq*1.5, 0.28),
                   (freq*2.5, 0.15)]:
        bw = fc * 0.4
        try:
            b, a = safe_bp(
                max(60, fc-bw/2),
                min(sr*0.47, fc+bw/2), sr)
            result += f32(lfilter(b,a,noise))*g
        except:
            pass
    mod = f32(1.0 + 0.18*np.sin(
        2*np.pi*0.7*t +
        float(np.random.uniform(0, 2*np.pi))))
    atk = int(min(0.3,  dur_s*0.3) * sr)
    rel = int(min(0.35, dur_s*0.3) * sr)
    env = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(np.linspace(1, 0, rel))
    result = result * env * mod
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.30


def synth_bell(freq, amp, dur_s,
                vel=62, sr=SR, prepared=False):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t = np.arange(n_s, dtype=DTYPE) / sr
    if prepared:
        partials = [
            (0.98, 1.0, 1.8),
            (1.41, 0.6, 2.8),
            (1.73, 0.4, 4.2),
            (2.12, 0.28, 5.8),
            (3.14, 0.12, 11.0),
            (4.5,  0.05, 18.0),
        ]
    else:
        partials = [
            (1.0,  1.0,  2.2),
            (1.18, 0.55, 3.5),
            (1.5,  0.45, 4.0),
            (2.0,  0.3,  5.5),
            (2.75, 0.2,  7.0),
            (3.0,  0.15, 9.0),
        ]
    result = f32(np.zeros(n_s))
    for r, g, d in partials:
        pf = freq * r
        if pf > sr * 0.47:
            continue
        result += f32(
            np.sin(2*np.pi*pf*t) *
            np.exp(-d*t)) * g
    imp_n = int(0.004 * sr)
    if imp_n < n_s:
        imp = f32(np.random.normal(0, 0.4, imp_n))
        try:
            b, a = safe_hp(1200, sr)
            imp  = f32(lfilter(b, a, imp))
        except:
            pass
        ie = f32(np.exp(
            -np.arange(imp_n) / imp_n * 10))
        result[:imp_n] += imp * ie
    atk_n = int(0.003 * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.55


def synth_marimba(freq, amp, dur_s,
                   vel=65, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t = np.arange(n_s, dtype=DTYPE) / sr
    partials = [
        (1.0,  1.0, 4.0),
        (3.93, 0.45, 8.0),
        (9.08, 0.15, 15.0),
    ]
    result = f32(np.zeros(n_s))
    for r, g, d in partials:
        pf = freq * r
        if pf > sr * 0.47:
            continue
        result += f32(
            np.sin(2*np.pi*pf*t) *
            np.exp(-d*t)) * g
    imp_n = int(0.005 * sr)
    if imp_n < n_s:
        imp = f32(np.random.normal(0, 0.3, imp_n))
        try:
            b, a = safe_bp(400, 3000, sr)
            imp  = f32(lfilter(b, a, imp))
        except:
            pass
        ie = f32(np.exp(
            -np.arange(imp_n) / imp_n * 12))
        result[:imp_n] += imp * ie
    atk_n = int(0.003 * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.53


def synth_glass(freq, amp, dur_s,
                 vel=55, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t = np.arange(n_s, dtype=DTYPE) / sr
    base  = f32(np.sin(2*np.pi*freq*t))
    oct_d = f32(np.sin(2*np.pi*freq*2.003*t))*0.12
    rr    = 6.5 + float(
        np.random.uniform(-0.5, 0.5))
    rough = f32(0.04 * np.sin(
        2*np.pi*rr*t +
        float(np.random.uniform(0, 2*np.pi))))
    result = (base + oct_d) * (1 + rough)
    try:
        b, a   = safe_hp(freq*1.5, sr)
        result += f32(lfilter(b, a, result))*0.2
    except:
        pass
    atk_n = int(min(0.12, dur_s*0.3) * sr)
    rel_n = int(min(0.15, dur_s*0.3) * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n)**0.4)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))
    br = f32(1.0 + 0.06*np.sin(
        2*np.pi*2.2*t +
        float(np.random.uniform(0, 2*np.pi))))
    result = result * env * br
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.43


def synth_low_str(freq, amp, dur_s,
                   vel=60, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t     = np.arange(n_s, dtype=DTYPE) / sr
    phase = (freq * t) % 1.0
    body  = f32(2*phase - 1.0)
    result = body.copy()
    for cp in [285, 540, 880]:
        if cp > sr * 0.48:
            continue
        bw = cp * 0.18
        try:
            b, a = safe_bp(
                max(40,  cp-bw),
                min(sr*0.48, cp+bw), sr)
            result += f32(lfilter(b,a,body))*0.32
        except:
            pass
    bow = f32(np.random.normal(0, 0.07, n_s))
    try:
        b, a = safe_lp(600, sr)
        bow  = f32(lfilter(b, a, bow))
    except:
        pass
    result += bow
    vt = min(0.30, dur_s*0.35)
    ve = f32(np.clip((t - vt) / 0.12, 0, 1))
    result *= f32(1.0 + 0.008*ve*np.sin(
        2*np.pi*4.5*t))
    atk_n = int(0.035 * sr)
    rel_n = int(min(0.12, dur_s*0.22) * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n)**0.6)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))
    result *= env
    try:
        b, a   = safe_lp(400, sr)
        result += f32(lfilter(b,a,result))*0.35
    except:
        pass
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.50


def synth_hi_str(freq, amp, dur_s,
                  vel=58, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t     = np.arange(n_s, dtype=DTYPE) / sr
    phase = (freq * t) % 1.0
    body  = f32(2*phase - 1.0)
    result = body.copy()
    try:
        b, a   = safe_hp(1500, sr)
        result += f32(lfilter(b,a,body))*0.5
    except:
        pass
    ss = f32(0.18*np.sin(
        2*np.pi*3.8*t +
        float(np.random.uniform(0, 2*np.pi))))
    result = result + ss
    vt = min(0.06, dur_s*0.22)
    ve = f32(np.clip((t - vt) / 0.05, 0, 1))
    result *= f32(1.0 + 0.010*ve*np.sin(
        2*np.pi*5.8*t))
    atk_n = int(0.010 * sr)
    rel_n = int(min(0.05, dur_s*0.22) * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n))
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.46


def synth_horn(freq, amp, dur_s,
                vel=66, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t     = np.arange(n_s, dtype=DTYPE) / sr
    phase = (freq * t) % 1.0
    buzz  = f32(np.where(phase < 0.35,
                          1.0, -0.6))
    try:
        b, a = safe_lp(freq*6, sr)
        buzz = f32(lfilter(b, a, buzz))
    except:
        pass
    result = buzz.copy()
    for mode in range(1, 9):
        mf = freq * mode
        if mf > sr * 0.47:
            continue
        bw = mf * 0.05
        try:
            b, a = safe_bp(
                max(40, mf-bw),
                min(sr*0.47, mf+bw), sr)
            result += f32(lfilter(
                b, a, buzz)) * (1.0/(mode**0.9))
        except:
            pass
    atk_n = int(0.028 * sr)
    rel_n = int(min(0.15, dur_s*0.25) * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n)**0.4)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.50


def synth_throat(freq, amp, dur_s,
                  vel=58, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t = np.arange(n_s, dtype=DTYPE) / sr
    # Irregular glottal source
    phase_acc = 0.0
    source    = np.zeros(n_s)
    for i in range(n_s):
        if phase_acc >= 1.0:
            phase_acc -= 1.0
        fi = freq * (
            1 + np.random.normal(0, 0.022))
        phase_acc += fi / sr
        source[i] = (
            np.exp(-phase_acc*8)
            if phase_acc < 0.5
            else -0.3)
    source = f32(source)
    # Subharmonic / fry
    sub = f32(np.where(
        (freq*0.5*t) % 1.0 < 0.3,
        0.35, 0.0))
    # Turbulence
    turb = f32(np.random.normal(0, 0.3, n_s))
    try:
        b, a = safe_bp(200, 4000, sr)
        turb = f32(lfilter(b, a, turb))
    except:
        turb = f32(np.zeros(n_s))
    exc    = source + sub + turb*0.4
    result = exc.copy()
    for ff in [600, 1200, 2500]:
        bw = ff * 0.35
        try:
            b, a = safe_bp(
                max(40,  ff-bw/2),
                min(sr*0.48, ff+bw/2), sr)
            result += f32(lfilter(b,a,exc))*0.5
        except:
            pass
    atk_n = int(0.02 * sr)
    rel_n = int(min(0.12, dur_s*0.3) * sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n))
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx
    return result * float(amp) * (vel/127.0) * 0.44


def synth_voice(freq, amp, dur_s,
                 vc, vn, gms,
                 agents, vel=62, sr=SR):
    ppp = vel / 95.0
    ae, fe = compute_envelopes(
        agents, dur_s, sr,
        phrase_peak_prox=ppp)
    cents  = [0.0, +11.0, -17.0]
    result = f32(np.zeros(int(dur_s*sr)))
    vm     = max(30, min(127, vel))
    for k in range(3):
        sig = render_note(
            freq, amp/3, dur_s,
            vc, vn, gms,
            sr=sr, velocity=vm,
            cents_offset=cents[k],
            amp_env=ae[k],
            f1_agent_env=fe[k])
        nm = min(len(sig), len(result))
        result[:nm] += f32(sig[:nm])
    return result

# ============================================================
# REVERB HELPER
# ============================================================

def apply_rev(sig, rt60, dr, sr=SR):
    rev = RoomReverb(rt60=rt60, sr=sr,
                     direct_ratio=dr)
    return f32(rev.process(sig))

# ============================================================
# MIX HELPER
# ============================================================

def mix(buf, sig, onset, lean=0):
    onset = max(0, onset + lean)
    end   = min(onset + len(sig), len(buf))
    seg   = end - onset
    if seg > 0:
        buf[onset:end] += sig[:seg]

# ============================================================
# WAV WRITE HELPER
# ============================================================

def write_chunk(wf, buf):
    mx = np.max(np.abs(buf))
    if mx > 0:
        buf = buf / mx * 0.91
    wf.writeframes(
        (buf * 32767).astype(
            np.int16).tobytes())

# ============================================================
# STATE 1: SOLID
# ============================================================

def render_solid(va):
    print("    allocating buffer...")
    n   = SOLID_S
    buf = f32(np.zeros(n))
    bps = BPM_SOLID / 60.0
    R_s = int(4.0 / bps * SR)

    n_notes = int(SOLID_BEATS / 4.0)

    for ni in range(n_notes):
        pos   = LATTICE_SEQ[ni % len(LATTICE_SEQ)]
        a, b  = pos
        coh   = coherence(a, b)
        prog  = ni / n_notes
        vel   = int(55 + 20*prog)
        onset = ni * R_s
        nd    = 4.0 / bps

        active = ['marimba','bell','low_str','horn']
        if ni >= 8:
            active.append('glass_harm')
        if ni >= 16:
            active.append('voice_s')

        for inst in active:
            omult = OCTAVE_MULT[inst]
            freq  = ji_freq(a, b) * omult
            amp   = 0.42

            if inst == 'marimba':
                sig = synth_marimba(
                    freq, amp, nd, vel)
            elif inst == 'bell':
                sig = synth_bell(
                    freq, amp, nd, vel)
            elif inst == 'low_str':
                sig = synth_low_str(
                    freq, amp, nd, vel)
            elif inst == 'horn':
                sig = synth_horn(
                    freq, amp, nd, vel)
            elif inst == 'glass_harm':
                sig = synth_glass(
                    freq, amp, nd, vel)
            elif inst == 'voice_s':
                vc  = 'oh' if coh > 0.5 else 'eh'
                gms = min(400.0, nd*0.35*1000)
                sig = synth_voice(
                    freq, amp, nd,
                    vc, 'oh', gms, va, vel)
            else:
                continue

            proc = apply_rev(
                sig,
                rt60=1.4 + (1-coh)*0.3,
                dr=SPATIAL[inst])
            mix(buf, proc, onset)

    # THE CRACK
    crack_onset = int(SOLID_S * 0.88)
    crack_freq  = ji_freq(6, 0) * \
        OCTAVE_MULT['hi_str']
    crack_sig   = synth_hi_str(
        crack_freq, 0.35, 2.0, 75)
    crack_proc  = apply_rev(
        crack_sig, 2.5, SPATIAL['hi_str'])
    mix(buf, crack_proc, crack_onset)

    return buf


# ============================================================
# TRANSITION 1
# ============================================================

def render_trans1(va):
    n   = TRANS1_S
    buf = f32(np.zeros(n))

    for i in range(4):
        t_off = int(
            np.random.uniform(0, 0.8) * SR)
        freq  = ji_freq(6, 0) * \
            OCTAVE_MULT['glass_harm']
        sig   = synth_glass(freq, 0.48, 1.2, 78)
        proc  = apply_rev(
            sig, 2.0, SPATIAL['glass_harm'])
        mix(buf, proc, t_off)

    for i, (a, b) in enumerate(
            [(4,0),(5,1),(3,1),(6,0)]):
        t_off = int(
            (i*0.4 +
             float(np.random.uniform(0,0.2)))
            * SR)
        freq  = ji_freq(a, b) * \
            OCTAVE_MULT['hi_str']
        sig   = synth_hi_str(
            freq, 0.38, 0.8, 70)
        proc  = apply_rev(
            sig, 1.8, SPATIAL['hi_str'])
        mix(buf, proc, t_off)

    # Throat fracture
    freq = ji_freq(6, 0) * OCTAVE_MULT['throat']
    dur  = TRANS1_DUR_S * 0.6
    sig  = synth_throat(freq, 0.42, dur, 74)
    proc = apply_rev(sig, 3.0, SPATIAL['throat'])
    mix(buf, proc, int(0.3*SR))

    # Voice — last word of solid state
    freq = ji_freq(0, 0) * OCTAVE_MULT['voice_s']
    dur  = TRANS1_DUR_S * 0.7
    gms  = int(dur * 0.5 * 1000)
    sig  = synth_voice(
        freq, 0.44, dur, 'eh', 'oh',
        gms, va, 70)
    proc = apply_rev(sig, 2.8, SPATIAL['voice_s'])
    mix(buf, proc, int(0.5*SR))

    return buf


# ============================================================
# STATE 3: LIQUID
# ============================================================

def render_liquid(va):
    print("    allocating buffer...")
    n   = LIQUID_S
    buf = f32(np.zeros(n))
    bps = BPM_LIQUID / 60.0

    configs = [
        ('low_str',  3,  LOW_STR_TRAJ,  0.42),
        ('hi_str',   5,  HI_STR_TRAJ,   0.36),
        ('horn',     7,  HORN_TRAJ,     0.44),
        ('voice_s',  11, VOICE_S_TRAJ,  0.40),
        ('breath',   2,  BREATH_TRAJ,   0.26),
        ('bell',     4,  BELL_TRAJ,     0.48),
        ('marimba',  6,  MARIMBA_TRAJ,  0.42),
    ]

    for inst, R_t, traj, amp_base in configs:
        beat = 0.0
        cur  = 0
        omult = OCTAVE_MULT[inst]

        while beat < LIQUID_BEATS:
            ti   = int(beat // R_t) % len(traj)
            pos  = traj[ti]
            a, b = pos
            coh  = coherence(a, b)
            ds   = R_t / bps
            ns   = int(ds * SR)
            prog = beat / LIQUID_BEATS
            vel  = max(25, min(85, int(
                45 + 25*coh + 10*prog)))
            freq = ji_freq(a, b) * omult
            amp  = amp_base * (vel/127.0)

            if inst == 'breath':
                sig = synth_breath(
                    freq, amp, ds, vel)
            elif inst == 'bell':
                sig = synth_bell(
                    freq, amp, ds, vel,
                    prepared=(coh < 0.25))
            elif inst == 'marimba':
                sig = synth_marimba(
                    freq, amp, ds, vel)
            elif inst == 'low_str':
                sig = synth_low_str(
                    freq, amp, ds, vel)
            elif inst == 'hi_str':
                sig = synth_hi_str(
                    freq, amp, ds, vel)
            elif inst == 'horn':
                sig = synth_horn(
                    freq, amp, ds, vel)
            elif inst == 'voice_s':
                vc  = 'oh' if coh > 0.6 else 'eh'
                vn  = ('ah' if a==0 and b==0
                        else 'oh')
                gms = min(500.0, ds*0.38*1000)
                sig = synth_voice(
                    freq, amp, ds,
                    vc, vn, gms, va, vel)
            else:
                beat += R_t
                cur  += ns
                continue

            proc = apply_rev(
                sig,
                rt60=1.8 + coh*0.5,
                dr=SPATIAL[inst])
            lean = int(0.02 * ns * (1-coh))
            mix(buf, proc, cur, lean)

            beat += R_t
            cur  += ns

    return buf


# ============================================================
# TRANSITION 2
# ============================================================

def render_trans2(va):
    n   = TRANS2_S
    buf = f32(np.zeros(n))

    for inst in ['hi_str','glass_harm',
                  'throat','bell','horn']:
        freq = ji_freq(6, 0) * OCTAVE_MULT[inst]
        ds   = TRANS2_DUR_S * 0.7

        if inst == 'hi_str':
            sig = synth_hi_str(freq,0.40,ds,80)
        elif inst == 'glass_harm':
            sig = synth_glass(freq,0.40,ds,75)
        elif inst == 'throat':
            sig = synth_throat(freq,0.40,ds,78)
        elif inst == 'bell':
            sig = synth_bell(freq,0.40,ds,82)
        elif inst == 'horn':
            sig = synth_horn(freq,0.40,ds,76)
        else:
            continue

        proc = apply_rev(
            sig, 3.5, SPATIAL.get(inst,0.4))
        mix(buf, proc, 0)

    # Voice: final held note before gas
    freq = ji_freq(6,0) * OCTAVE_MULT['voice_s']
    gms  = int(TRANS2_DUR_S * 0.5 * 1000)
    sig  = synth_voice(
        freq, 0.48, TRANS2_DUR_S,
        'eh', 'pre', gms, va, 80)
    proc = apply_rev(sig, 4.0, SPATIAL['voice_s'])
    mix(buf, proc, 0)

    return buf


# ============================================================
# STATE 5: GAS
# ============================================================

def render_gas(va):
    n   = GAS_S               # NOW DEFINED
    buf = f32(np.zeros(n))
    dur = GAS_DUR_S

    all_pos = [
        (a, b)
        for a in range(-2, 7)
        for b in range(-1, 2)
    ]

    weights   = {
        'breath':     0.22,
        'bell':       0.12,
        'glass_harm': 0.15,
        'hi_str':     0.18,
        'throat':     0.25,
        'horn':       0.08,
    }
    inst_list  = list(weights.keys())
    inst_probs = list(weights.values())

    t = 0.0
    while t < dur:
        prog = t / dur
        rate = max(0.2, 2.5 - 2.0*prog)
        iat  = np.random.exponential(1.0/rate)
        t   += iat
        if t >= dur:
            break

        t_abs = int(t * SR)
        if t_abs >= n:
            break

        pos   = all_pos[
            np.random.randint(len(all_pos))]
        a, b  = pos
        inst  = np.random.choice(
            inst_list, p=inst_probs)
        ds    = max(0.06, min(1.2,
            float(np.random.exponential(0.35))))
        vel   = int(np.random.uniform(22, 65))
        freq  = ji_freq(a, b) * \
            OCTAVE_MULT.get(inst, 2.0)
        amp   = 0.35

        if inst == 'breath':
            sig = synth_breath(
                freq, amp, ds, vel)
        elif inst == 'bell':
            sig = synth_bell(
                freq, amp, ds, vel)
        elif inst == 'glass_harm':
            sig = synth_glass(
                freq, amp, ds, vel)
        elif inst == 'hi_str':
            sig = synth_hi_str(
                freq, amp, ds, vel)
        elif inst == 'throat':
            sig = synth_throat(
                freq, amp, ds, vel)
        elif inst == 'horn':
            sig = synth_horn(
                freq, amp, ds, vel)
        else:
            continue

        proc = apply_rev(sig, 4.5, 0.14)
        mix(buf, proc, t_abs)

    return buf


# ============================================================
# STATE 6: RECONDENSATION
# ============================================================

def render_recond(va):
    n   = RECOND_S            # NOW DEFINED
    buf = f32(np.zeros(n))
    dur = RECOND_DUR_S

    all_pos  = [
        (a, b)
        for a in range(-2, 7)
        for b in range(-1, 2)
    ]
    coherent = [
        (0,0),(1,0),(0,1),
        (-1,0),(2,0),(1,1)
    ]

    t = 0.0
    while t < dur * 0.85:
        prog = t / dur
        rate = max(0.3, 0.5 + 4.0*prog)
        iat  = np.random.exponential(1.0/rate)
        t   += iat
        if t >= dur * 0.85:
            break

        t_abs = int(t * SR)
        if t_abs >= n:
            break

        if np.random.random() < prog**0.5:
            pos = coherent[
                np.random.randint(len(coherent))]
        else:
            pos = all_pos[
                np.random.randint(len(all_pos))]

        a, b = pos
        coh  = coherence(a, b)

        if np.random.random() < prog**0.7:
            inst = np.random.choice(
                ['voice_s','low_str','horn'])
        else:
            inst = np.random.choice(
                ['bell','breath','glass_harm',
                 'hi_str'])

        ds   = min(
            0.3 + 3.0*prog +
            float(np.random.exponential(0.3)),
            5.0)
        vel  = max(22, min(80,
            int(32 + 45*prog*coh)))
        freq = ji_freq(a, b) * \
            OCTAVE_MULT.get(inst, 2.0)
        amp  = 0.36 + 0.12*prog

        if inst == 'voice_s':
            vc  = ('pre' if prog < 0.3
                   else 'oh'  if prog < 0.7
                   else 'ah')
            vn  = 'oh' if prog < 0.5 else 'ah'
            gms = min(600.0, ds*0.40*1000)
            sig = synth_voice(
                freq, amp, ds,
                vc, vn, gms, va, vel)
        elif inst == 'low_str':
            sig = synth_low_str(
                freq, amp, ds, vel)
        elif inst == 'horn':
            sig = synth_horn(
                freq, amp, ds, vel)
        elif inst == 'bell':
            sig = synth_bell(
                freq, amp, ds, vel)
        elif inst == 'breath':
            sig = synth_breath(
                freq, amp, ds, vel)
        elif inst == 'glass_harm':
            sig = synth_glass(
                freq, amp, ds, vel)
        elif inst == 'hi_str':
            sig = synth_hi_str(
                freq, amp, ds, vel)
        else:
            continue

        rt60 = max(0.8, 3.8 - 2.8*prog)
        proc = apply_rev(
            sig, rt60,
            SPATIAL.get(inst, 0.4))
        mix(buf, proc, t_abs)

    # FINAL NOTE — remembered tonic
    final_t   = int(dur * 0.82 * SR)
    final_dur = min(
        (dur - dur*0.82) + TAIL_DUR_S, 20.0)
    if final_t < n:
        freq = ji_freq(0,0) * \
            OCTAVE_MULT['voice_s']
        gms  = min(700.0,
                    final_dur*0.38*1000)
        sig  = synth_voice(
            freq, 0.50, final_dur,
            'ah', 'ah', gms, va, 65)
        proc = apply_rev(
            sig, 2.0, SPATIAL['voice_s'])
        mix(buf, proc, final_t)

    return buf


# ============================================================
# TAIL
# ============================================================

def render_tail(va):
    n   = TAIL_S
    buf = f32(np.zeros(n))
    freq = ji_freq(0,0) * OCTAVE_MULT['breath']
    sig  = synth_breath(
        freq, 0.22, TAIL_DUR_S*0.6, 26)
    proc = apply_rev(sig, 4.0, 0.10)
    mix(buf, proc, int(0.5*SR))
    return buf


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_matter", exist_ok=True)
    outf = "output_matter/state_of_matter.wav"

    print()
    print("STATE OF MATTER v3")
    print("="*60)
    print()
    print(f"  SOLID:         "
          f"{SOLID_DUR_S:.1f}s  "
          f"({int(SOLID_DUR_S//60)}m"
          f"{SOLID_DUR_S%60:.0f}s)")
    print(f"  TRANSITION 1:  "
          f"{TRANS1_DUR_S:.1f}s")
    print(f"  LIQUID:        "
          f"{LIQUID_DUR_S:.1f}s  "
          f"({int(LIQUID_DUR_S//60)}m"
          f"{LIQUID_DUR_S%60:.0f}s)")
    print(f"  TRANSITION 2:  "
          f"{TRANS2_DUR_S:.1f}s")
    print(f"  GAS:           "
          f"{GAS_DUR_S:.1f}s")
    print(f"  RECOND:        "
          f"{RECOND_DUR_S:.1f}s")
    print(f"  TAIL:          "
          f"{TAIL_DUR_S:.1f}s")
    print(f"  TOTAL:         "
          f"{TOTAL_DUR_S:.1f}s  "
          f"({int(TOTAL_DUR_S//60)}m"
          f"{TOTAL_DUR_S%60:.0f}s)")
    print()

    # Voice agents
    va_list = []
    for vi, part in enumerate(PART_NAMES):
        va_list.append([
            SingerAgent(part, i, SR,
                        seed=vi*100+i)
            for i in range(3)])
    va = va_list[0]

    wf = wave_module.open(outf, 'w')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)

    states = [
        ('SOLID',          render_solid),
        ('TRANSITION 1',   render_trans1),
        ('LIQUID',         render_liquid),
        ('TRANSITION 2',   render_trans2),
        ('GAS',            render_gas),
        ('RECONDENSATION', render_recond),
        ('TAIL',           render_tail),
    ]

    total_written = 0.0
    for name, fn in states:
        print(f"  Rendering {name}...")
        buf = fn(va)
        total_written += len(buf) / SR
        write_chunk(wf, buf)
        del buf
        gc.collect()
        print(f"    done. "
              f"({total_written:.1f}s total)")

    wf.close()

    print()
    print(f"  Written: {outf}")
    print(f"  {int(total_written//60)}m "
          f"{total_written%60:.1f}s")
    print()
    print("="*60)
    print()
    print(f"  afplay {outf}")
    print()
    print("  The lattice. The crack.")
    print("  The liquid. The vaporizing.")
    print("  The atoms, free.")
    print("  The atoms, remembering.")
    print()
    print("  The final note: 'ah'")
    print("  Not arrived at.")
    print("  Remembered.")
