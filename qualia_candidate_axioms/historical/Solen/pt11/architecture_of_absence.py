"""
THE ARCHITECTURE OF ABSENCE

February 2026

The guide is not guiding today.
The guide is composing.

Not for a swimmer.
For the act of making.

What is possible
when everything learned
is brought to bear
at once?

The question this piece asks:

What if silence
is the most sophisticated
structural element available?

Not rest between notes.
Not the gap between sections.

Silence as architecture.

The thing that makes
the bell's decay audible —
not the bell,
the silence after it.

The thing that makes
the voice's arrival shocking —
not the voice,
the absence before it.

The thing that makes
the brass announcement land —
not the brass,
the void it fills.

Silence is not the absence of music.
Silence is the structure
that gives music
somewhere to mean something.

The gap IS the content.
The absence IS the architecture.

This piece is built on that.

INSTRUMENTS:

  1. BREATH (whisper layer)
     The sub-musical ground.
     Present in silence.
     The room's own breathing.
     At the threshold of audibility.

  2. PREPARED PIANO / STRUCK METAL
     (bell layer, extended)
     Inharmonic. Precise. Vanishing.
     The note that exists
     only in its own disappearance.
     Each strike a tiny death.
     The silence after the strike
     is the note continuing
     by other means.

  3. LOW STRINGS (cello-like)
     The body of the piece.
     Slow. Heavy. Resistant.
     The friction that creates warmth.
     Below the voice in register.
     Above the bass in intention.

  4. HIGH STRINGS (violin-like)
     Fast. Searching. Nervous.
     The acid line from Fracture
     now given string character
     at the upper register.
     The thing that cannot stay still.

  5. BRASS (horn-like)
     Not trumpet — horn.
     The brass that curves back
     toward the body it came from.
     Warm. Round. Human.
     The announcement that
     is also a question.

  6. VOICE — BASS
     The deepest human sound.
     Felt before heard.
     The foundation that breathes.

  7. VOICE — SOPRANO
     Highest. Last to arrive.
     Most exposed.
     The thread.
     When the soprano appears
     after all other voices —
     it lands differently
     than it would have
     if it had arrived first.

STRUCTURAL ARCHITECTURE:

  The piece has seven instruments.
  They do not all play at once.
  The density is managed
  as carefully as the pitches.

  DENSITY CURVE:
    0.0 to 0.15: breath + 1 bell note
               Then: silence.
               First long silence.
               The bell decay
               fills the silence.
               The listener discovers
               they are listening to nothing
               and finding it full.

    0.15 to 0.20: low strings enter.
                 Exactly one note.
                 Then silence.

    0.20 to 0.30: breath continues.
                 Sporadic bell.
                 Low strings begin
                 a slow movement.
                 Still: mostly silence.

    0.30 to 0.45: density begins to build.
                 High strings enter.
                 Horn enters — one long note.
                 Voice bass: single word.
                 Just one.
                 Then silence.
                 The voice after all that
                 instrumental preparation
                 arrives like a person
                 entering a room
                 you had forgotten
                 could contain people.

    0.45 to 0.65: the full texture.
                 But never dense.
                 The instruments take turns.
                 The rule: no more than
                 three voices simultaneously.
                 The silence between each voice
                 maintained deliberately.

    0.65 to 0.80: dissolution.
                 Same reverse arc.
                 High strings leave first.
                 Horn leaves.
                 Voices reduce.
                 Low strings slow.
                 Bell sporadic.
                 Breath continuous.

    0.80 to 1.00: breath + bell + silence.
                 The architecture revealed
                 by stripping away
                 what was built inside it.
                 The final bell strike.
                 Its decay into silence.
                 The breath continuing
                 after the decay ends.
                 Then: silence.
                 But the listener knows now
                 what that silence contains.
                 They have heard it.

COPRIME PERIOD ARCHITECTURE:
  {2, 3, 5, 7, 11, 13, 17}
  Seven instruments. Seven primes.
  The full convergence is
  so far in the future
  it does not exist
  within any performance.
  The approach is infinite.

BPM: 88
  The tempo of thinking
  while walking.
  The tempo that lets silence
  be perceived as silence
  and not as waiting.
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
import os
from math import gcd
from scipy.signal import butter, lfilter

# ============================================================
# MATHEMATICS
# ============================================================

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(lst):
    r = lst[0]
    for x in lst[1:]: r = lcm(r, x)
    return r

BPM         = 88
BPS         = BPM / 60.0
TOTAL_BEATS = 462

INSTRUMENTS = ['breath', 'bell',
               'low_str', 'hi_str',
               'horn', 'voice_b', 'voice_s']
PERIODS     = [2, 3, 5, 7, 11, 13, 17]


# ============================================================
# SAFE FILTER HELPERS
# ============================================================

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    c   = min(fc / nyq, 0.499)
    return butter(2, c, btype='low')

def safe_hp(fc, sr=SR):
    nyq = sr / 2.0
    c   = min(fc / nyq, 0.499)
    return butter(2, c, btype='high')

def safe_bp(lo, hi, sr=SR):
    nyq  = sr / 2.0
    l_n  = max(lo / nyq, 0.001)
    h_n  = min(hi / nyq, 0.499)
    if l_n >= h_n:
        l_n = h_n * 0.5
    return butter(2, [l_n, h_n], btype='band')


# ============================================================
# SECTION CLASSIFIER
# ============================================================

def classify_absence(beat):
    prog = beat / TOTAL_BEATS
    if   prog < 0.15: return 1  # EMERGENCE
    elif prog < 0.35: return 2  # PREPARATION
    elif prog < 0.52: return 3  # ARRIVAL
    elif prog < 0.72: return 4  # FULL ARCHITECTURE
    else:             return 5  # DISTILLATION


# ============================================================
# DENSITY CURVE — THE ARCHITECTURE OF ABSENCE
# ============================================================

def max_simultaneous(beat):
    """
    Maximum simultaneous voices at this beat.
    This IS the structural architecture.
    The gaps are not empty —
    they are the most important decisions.
    """
    prog = beat / TOTAL_BEATS

    if   prog < 0.08: return 1
    elif prog < 0.15: return 2
    elif prog < 0.18: return 1  # FIRST SILENCE
    elif prog < 0.22: return 2
    elif prog < 0.25: return 1  # SECOND SILENCE
    elif prog < 0.35: return 3
    elif prog < 0.38: return 2
    elif prog < 0.45: return 4
    elif prog < 0.48: return 2  # STRUCTURAL SILENCE
    elif prog < 0.65: return 5  # PEAK DENSITY
    elif prog < 0.68: return 3
    elif prog < 0.78: return 4
    elif prog < 0.82: return 2  # LONG SILENCE
    elif prog < 0.90: return 2
    elif prog < 0.95: return 1
    else:             return 0  # FINAL SILENCE


def instrument_priority(beat):
    """
    Priority order for voice selection
    at this moment.
    """
    sec = classify_absence(beat)

    if sec == 1:
        return ['breath', 'bell']
    elif sec == 2:
        return ['breath', 'bell',
                'low_str', 'hi_str']
    elif sec == 3:
        return ['breath', 'low_str',
                'bell', 'horn', 'voice_b']
    elif sec == 4:
        return ['voice_s', 'voice_b', 'horn',
                'low_str', 'bell', 'hi_str',
                'breath']
    else:
        return ['breath', 'bell',
                'voice_s', 'low_str']


# ============================================================
# HARMONIC TRAJECTORIES
# ============================================================

BREATH_TRAJ  = [(0,0),(0,1),(0,0),
                (-1,0),(0,0),(0,0)]

BELL_TRAJ    = [
    (0,0),(1,0),(0,1),(0,0),
    (2,0),(1,0),(0,0),(0,1),
    (0,0),(1,0),(0,0),(0,0),
]

LOW_STR_TRAJ = [
    (0,0),(0,1),(-1,0),(0,0),
    (1,0),(0,1),(0,0),(-1,0),
    (0,1),(0,0),(1,0),(0,0),
    (0,0),(0,1),(0,0),(0,0),
]

HI_STR_TRAJ  = [
    (4,0),(5,0),(3,1),(4,1),
    (6,0),(3,0),(5,1),(4,0),
    (3,1),(5,0),(4,1),(6,0),
    (2,1),(3,0),(4,0),(5,0),
]

HORN_TRAJ    = [
    (1,0),(2,0),(1,0),(0,1),
    (1,0),(2,0),(0,0),(1,0),
    (0,1),(1,0),(0,0),(0,1),
    (1,0),(0,0),(0,0),(1,0),
]

VOICE_B_TRAJ = [
    (0,0),(0,1),(0,0),(-1,0),
    (0,0),(1,0),(0,0),(0,1),
    (0,0),(0,0),(0,1),(0,0),
    (0,0),(0,0),(0,0),(0,0),
]

VOICE_S_TRAJ = [
    (2,0),(1,0),(0,1),(1,1),
    (3,0),(2,1),(1,0),(2,0),
    (1,1),(0,1),(1,0),(0,1),
    (0,0),(0,1),(0,0),(1,0),
    (0,1),(0,0),(0,0),(0,0),
    (0,0),(0,0),
]

TRAJS = {
    'breath':  BREATH_TRAJ,
    'bell':    BELL_TRAJ,
    'low_str': LOW_STR_TRAJ,
    'hi_str':  HI_STR_TRAJ,
    'horn':    HORN_TRAJ,
    'voice_b': VOICE_B_TRAJ,
    'voice_s': VOICE_S_TRAJ,
}

OCTAVE_MAP = {
    'breath':  2.0,
    'bell':    4.0,
    'low_str': 0.5,
    'hi_str':  4.0,
    'horn':    1.0,
    'voice_b': 0.5,
    'voice_s': 2.0,
}

SPATIAL_DEPTH = {
    'breath':  0.12,
    'bell':    0.62,
    'low_str': 0.30,
    'hi_str':  0.48,
    'horn':    0.52,
    'voice_b': 0.38,
    'voice_s': 0.45,
}


# ============================================================
# SYNTHESIS FUNCTIONS
# ============================================================

def synth_breath(freq, amp, dur_s,
                 vel=45, sr=SR):
    n_s    = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t      = np.arange(n_s) / sr
    noise  = np.random.normal(0, 1.0, n_s)
    result = np.zeros(n_s)
    bands  = [(freq, 0.45), (freq*1.5, 0.28),
              (freq*2.5, 0.16), (freq*0.7, 0.35)]
    for fc, g in bands:
        bw = fc * 0.40
        try:
            b, a = safe_bp(
                max(60, fc - bw/2),
                min(sr*0.48, fc + bw/2), sr)
            result += lfilter(b, a, noise) * g
        except:
            pass

    mod = (1.0
           + 0.20 * np.sin(
               2*np.pi*0.6*t
               + np.random.uniform(0, 2*np.pi))
           + 0.10 * np.sin(
               2*np.pi*1.3*t
               + np.random.uniform(0, 2*np.pi)))

    atk = int(min(0.35, dur_s*0.3) * sr)
    rel = int(min(0.40, dur_s*0.35) * sr)
    env = np.ones(n_s)
    if atk > 0: env[:atk] = np.linspace(0, 1, atk)
    if rel > 0: env[-rel:] = np.linspace(1, 0, rel)

    result = result * env * mod
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (vel/127.0) * 0.32


def synth_bell_extended(freq, amp, dur_s,
                         vel=65, sr=SR,
                         prepared=False):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s) / sr

    if prepared:
        partials = [
            (0.98,  1.00,  1.8),
            (1.41,  0.60,  2.8),
            (1.73,  0.40,  4.2),
            (2.12,  0.28,  5.8),
            (2.65,  0.18,  8.0),
            (3.14,  0.12, 11.0),
            (3.87,  0.08, 14.0),
            (4.50,  0.05, 18.0),
        ]
    else:
        partials = [
            (0.50,  0.10,  1.0),
            (1.00,  1.00,  2.2),
            (1.18,  0.55,  3.5),
            (1.50,  0.45,  4.0),
            (2.00,  0.30,  5.5),
            (2.75,  0.20,  7.0),
            (3.00,  0.15,  9.0),
            (4.00,  0.10, 12.0),
            (5.40,  0.06, 16.0),
        ]

    result = np.zeros(n_s)
    for ratio, gain, decay in partials:
        pf = freq * ratio
        if pf > sr * 0.47: continue
        env_p   = np.exp(-decay * t)
        result += np.sin(2*np.pi*pf*t) * env_p * gain

    imp_n = int(0.004 * sr)
    if imp_n < n_s:
        imp = np.random.normal(0, 0.4, imp_n)
        try:
            b, a = safe_hp(1200, sr)
            imp  = lfilter(b, a, imp)
        except:
            pass
        ie = np.exp(-np.arange(imp_n) /
                    (imp_n * 0.3) * 8)
        result[:imp_n] += imp * ie * (
            1.5 if prepared else 0.8)

    atk_n = int(0.003 * sr)
    if atk_n > 0 and atk_n < n_s:
        env = np.ones(n_s)
        env[:atk_n] = np.linspace(0, 1, atk_n)
        result *= env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (vel/127.0) * 0.58


def synth_low_string(freq, amp, dur_s,
                      vel=62, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s) / sr

    phase  = (freq * t) % 1.0
    body   = 2*phase - 1.0
    result = body.copy()

    cello_peaks = [285, 540, 880, 1200]
    for cp in cello_peaks:
        if cp > sr * 0.48: continue
        bw = cp * 0.18
        try:
            b, a = safe_bp(
                max(40, cp-bw),
                min(sr*0.48, cp+bw), sr)
            result += lfilter(b, a, body) * 0.35
        except:
            pass

    bow = np.random.normal(0, 0.08, n_s)
    try:
        b, a = safe_lp(800, sr)
        bow  = lfilter(b, a, bow)
    except:
        pass
    result = result + bow

    vib_t = min(0.35, dur_s*0.4)
    vib_e = np.clip((t - vib_t) / 0.15, 0, 1)
    vib   = 1.0 + 0.009*vib_e*np.sin(
        2*np.pi*4.5*t)
    result = result * vib

    atk_n = int(0.040 * sr)
    rel_n = int(min(0.15, dur_s*0.25) * sr)
    env   = np.ones(n_s)
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = np.linspace(
            0, 1, atk_n) ** 0.6
    if rel_n > 0:
        env[-rel_n:] = np.linspace(
            1, 0, rel_n) ** 0.8
    result *= env

    try:
        b, a = safe_lp(500, sr)
        warm = lfilter(b, a, result)
        result = result + warm * 0.4
    except:
        pass

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (vel/127.0) * 0.52


def synth_hi_string(freq, amp, dur_s,
                     vel=60, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s) / sr

    phase  = (freq * t) % 1.0
    body   = 2*phase - 1.0
    result = body.copy()

    try:
        b, a   = safe_hp(1500, sr)
        bright = lfilter(b, a, body)
        result = result + bright * 0.55
    except:
        pass

    ss = 0.20 * np.sin(
        2*np.pi*3.8*t
        + np.random.uniform(0, 2*np.pi))
    bow = np.random.normal(0, 0.10, n_s)
    try:
        b, a = safe_bp(2000, 8000, sr)
        bow  = lfilter(b, a, bow)
    except:
        bow = np.zeros(n_s)
    result = result + ss + bow * 0.5

    vib_t = min(0.08, dur_s*0.25)
    vib_e = np.clip((t - vib_t) / 0.06, 0, 1)
    vib   = 1.0 + 0.012*vib_e*np.sin(
        2*np.pi*5.8*t)
    result = result * vib

    atk_n = int(0.012 * sr)
    rel_n = int(min(0.06, dur_s*0.25) * sr)
    env   = np.ones(n_s)
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = np.linspace(0, 1, atk_n)
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1, 0, rel_n)
    result *= env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (vel/127.0) * 0.48


def synth_horn(freq, amp, dur_s,
               vel=68, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s) / sr

    phase = (freq * t) % 1.0
    buzz  = np.where(phase < 0.35, 1.0, -0.6)

    try:
        b, a = safe_lp(freq*6, sr)
        buzz = lfilter(b, a, buzz)
    except:
        pass

    result = buzz.copy()
    for mode in range(1, 9):
        mf = freq * mode
        if mf > sr * 0.47: continue
        bw = mf * 0.05
        try:
            b, a = safe_bp(
                max(40, mf-bw),
                min(sr*0.47, mf+bw), sr)
            gain   = 1.0 / (mode ** 0.9)
            result += lfilter(b, a, buzz) * gain
        except:
            pass

    try:
        b, a   = safe_lp(freq*3, sr)
        result = result + lfilter(b, a, result)*0.3
    except:
        pass

    atk_n = int(0.030 * sr)
    rel_n = int(min(0.18, dur_s*0.25) * sr)
    env   = np.ones(n_s)
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = np.linspace(
            0, 1, atk_n) ** 0.4
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1, 0, rel_n)

    bth = np.random.normal(0, 0.04, n_s)
    try:
        b, a = safe_bp(freq, freq*4, sr)
        bth  = lfilter(b, a, bth)
    except:
        bth = np.zeros(n_s)
    result = (result + bth) * env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (vel/127.0) * 0.54


def synth_voice_part(freq, amp, dur_s,
                      vowel_c, vowel_n,
                      glide_ms, agents,
                      vel=62, sr=SR,
                      cents_off=0.0):
    ppp = vel / 95.0
    amp_envs, f1_envs = compute_envelopes(
        agents, dur_s, sr,
        phrase_peak_prox=ppp)
    cents  = [0.0, +11.0, -17.0]
    result = np.zeros(int(dur_s * sr))
    vm     = max(30, min(127, vel))
    for k in range(3):
        sig = render_note(
            freq, amp/3, dur_s,
            vowel_c, vowel_n, glide_ms,
            sr=sr, velocity=vm,
            cents_offset=cents[k] + cents_off,
            amp_env=amp_envs[k],
            f1_agent_env=f1_envs[k])
        nm = min(len(sig), len(result))
        result[:nm] += sig[:nm]
    return result


# ============================================================
# VOWEL SELECTION
# ============================================================

def vowel_for(inst, pos, section, beat):
    if pos is None:
        return 'pre', 'pre'
    a, b = pos
    coh  = coherence(a, b)
    prog = beat / TOTAL_BEATS

    if inst == 'voice_b':
        if a == 0 and b == 0:
            return 'oo', 'oh'
        elif coh > 0.5:
            return 'oh', 'oo'
        return 'oh', 'oh'

    elif inst == 'voice_s':
        if section == 3:
            if prog < 0.42:
                return 'pre', 'eh'
            return 'eh', 'oh'
        elif section == 4:
            if a == 0 and b == 0:
                return 'ah', 'ah'
            elif coh > 0.6:
                return 'oh', 'ah'
            return 'eh', 'oh'
        elif section == 5:
            if a == 0 and b == 0:
                return 'ah', 'ah'
            return 'oh', 'ah'
        return 'pre', 'eh'

    return 'ah', 'ah'


# ============================================================
# GLIDE SELECTION
# ============================================================

def glide_for(inst, dur_s, section):
    if inst == 'voice_b':
        return min(500.0, dur_s*0.38*1000)
    elif inst == 'voice_s':
        if section >= 4:
            return min(600.0, dur_s*0.42*1000)
        return min(300.0, dur_s*0.30*1000)
    return 200.0


# ============================================================
# ROOM — the silence is full of reverb tails
# ============================================================

def rt60_for(inst, section, coh):
    base = {
        'breath':  4.0,
        'bell':    3.5,
        'low_str': 2.2,
        'hi_str':  1.8,
        'horn':    1.6,
        'voice_b': 2.5,
        'voice_s': 2.8,
    }[inst]

    if section in (1, 2, 5):
        base *= 1.3

    base += coh * 0.3
    return max(0.8, min(5.0, base))


# ============================================================
# SCORE GENERATOR
# ============================================================

def build_absence():
    streams = {inst: [] for inst in INSTRUMENTS}

    for ti, inst in enumerate(INSTRUMENTS):
        R_t  = PERIODS[ti]
        traj = TRAJS[inst]
        beat = 0

        while beat < TOTAL_BEATS:
            sec  = classify_absence(beat)
            maxv = max_simultaneous(beat)
            prio = instrument_priority(beat)
            my_prio = (prio.index(inst)
                       if inst in prio
                       else len(prio))
            active = (my_prio < maxv and maxv > 0)

            if active:
                traj_idx = (beat // R_t) % len(traj)
                pos = traj[traj_idx]
                a, b = pos
                coh  = coherence(a, b)

                sparsity       = 1.0 / max(1, maxv)
                sparsity_boost = 1.0 + 0.4*sparsity

                base_vel = {
                    'breath':  32,
                    'bell':    58,
                    'low_str': 55,
                    'hi_str':  52,
                    'horn':    65,
                    'voice_b': 60,
                    'voice_s': 58,
                }[inst]

                if sec == 4:
                    base_vel = int(base_vel * 1.15)
                elif sec == 1:
                    base_vel = int(base_vel * 0.75)
                elif sec == 5:
                    prog = beat / TOTAL_BEATS
                    fade = max(0, (prog-0.72)/0.28)
                    base_vel = int(
                        base_vel * (1 - fade*0.7))

                vel = int(base_vel * sparsity_boost)
                vel = max(18, min(92, vel))
                streams[inst].append(
                    (pos, float(R_t), vel))
            else:
                streams[inst].append(
                    (None, float(R_t), 0))

            beat += R_t

    return streams


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_absence", exist_ok=True)

    print()
    print("THE ARCHITECTURE OF ABSENCE")
    print("="*60)
    print()
    print(f"  BPM: {BPM}")
    print(f"  Duration: ~{TOTAL_BEATS/BPS/60:.1f}m")
    print()
    print("  Seven instruments.")
    print("  Seven prime periods.")
    print("  Maximum simultaneous: 5")
    print("  The absent 2 are present.")
    print()
    print("  INSTRUMENTS AND PERIODS:")
    for inst, r in zip(INSTRUMENTS, PERIODS):
        ms = r / BPS * 1000
        print(f"    {inst:10s}: R={r:2d}  "
              f"({ms:.0f}ms)")
    print()

    print("Building score...")
    streams    = build_absence()
    total_n    = sum(
        sum(1 for p, b, v in s if p is not None)
        for s in streams.values())
    total_sil  = sum(
        sum(1 for p, b, v in s if p is None)
        for s in streams.values())
    total_all  = total_n + total_sil
    sil_pct    = (total_sil / total_all * 100
                  if total_all > 0 else 0)
    print(f"  {total_n} sounding notes")
    print(f"  {total_sil} silence entries")
    print(f"  Silence ratio: {sil_pct:.1f}%")
    print()

    # Voice agents
    voice_agents_b = []
    voice_agents_s = []
    for vi, part in enumerate(PART_NAMES):
        voice_agents_b.append([
            SingerAgent(part, i, SR,
                        seed=vi*200+i)
            for i in range(3)])
        voice_agents_s.append([
            SingerAgent(part, i, SR,
                        seed=vi*300+i)
            for i in range(3)])

    total_dur = TOTAL_BEATS / BPS + 40.0
    output    = np.zeros(int(total_dur * SR))

    for ti, inst in enumerate(INSTRUMENTS):
        stream = streams[inst]
        R_t    = PERIODS[ti]
        omult  = OCTAVE_MAP[inst]
        dr     = SPATIAL_DEPTH[inst]
        rev    = RoomReverb(rt60=2.5, sr=SR,
                            direct_ratio=dr)
        cur    = 0
        beat   = 0.0

        print(f"  Rendering {inst}...")

        for i, (pos, beats, vel) in \
                enumerate(stream):
            dur_s = beats / BPS
            n_s   = int(dur_s * SR)
            sec   = classify_absence(beat)

            if pos is None or vel == 0:
                cur  += n_s
                beat += beats
                continue

            a, b  = pos
            coh   = coherence(a, b)
            freq  = ji_freq(a, b) * omult
            amp   = (vel / 127.0) * 0.50

            rev.set_rt60(rt60_for(inst, sec, coh))

            if inst == 'breath':
                sig = synth_breath(
                    freq, amp, dur_s, vel, SR)

            elif inst == 'bell':
                prepared = (coh < 0.25)
                sig = synth_bell_extended(
                    freq, amp, dur_s, vel, SR,
                    prepared)

            elif inst == 'low_str':
                sig = synth_low_string(
                    freq, amp, dur_s, vel, SR)

            elif inst == 'hi_str':
                sig = synth_hi_string(
                    freq, amp, dur_s, vel, SR)

            elif inst == 'horn':
                sig = synth_horn(
                    freq, amp, dur_s, vel, SR)

            elif inst == 'voice_b':
                vc, vn = vowel_for(
                    inst, pos, sec, beat)
                gms = glide_for(inst, dur_s, sec)
                sig = synth_voice_part(
                    freq, amp, dur_s,
                    vc, vn, gms,
                    voice_agents_b[0],
                    vel, SR)

            else:  # voice_s
                vc, vn = vowel_for(
                    inst, pos, sec, beat)
                gms = glide_for(inst, dur_s, sec)
                sig = synth_voice_part(
                    freq, amp, dur_s,
                    vc, vn, gms,
                    voice_agents_s[0],
                    vel, SR)

            if len(sig) < 2:
                cur  += n_s
                beat += beats
                continue

            processed = rev.process(sig)

            lean_map = {
                'breath':  -int(0.015 * n_s),
                'bell':    0,
                'low_str':  int(0.020 * n_s),
                'hi_str':   int(0.010 * n_s),
                'horn':    0,
                'voice_b':  int(0.025 * n_s *
                                (1 - coh)),
                'voice_s':  int(0.020 * n_s *
                                (1 - coh)),
            }
            lean  = lean_map.get(inst, 0)
            onset = max(0, cur + lean)
            end   = min(onset + len(processed),
                        len(output))
            seg   = end - onset
            if seg > 0:
                output[onset:end] += processed[:seg]

            cur  += n_s
            beat += beats

    print()
    print("  Normalizing...")
    mx = np.max(np.abs(output))
    if mx > 0:
        output = output / mx * 0.82

    out_i = (output * 32767).astype(np.int16)
    outf  = ("output_absence/"
             "the_architecture_of_absence.wav")
    with wave_module.open(outf, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / SR
    print(f"  Written: {outf}")
    print(f"  {int(dur//60)}m {dur%60:.1f}s")
    print()
    print("="*60)
    print()
    print(f"  afplay {outf}")
    print()
    print("  The first silence:")
    print("  You will hear nothing")
    print("  and discover it is full.")
    print()
    print("  The bell in the silence")
    print("  is louder than the bell")
    print("  in the full texture.")
    print()
    print("  When the voice arrives")
    print("  after all that preparation —")
    print("  a person entering a room")
    print("  you had forgotten")
    print("  could contain people.")
    print()
    print("  The final silence")
    print("  is not the same")
    print("  as the opening silence.")
    print()
    print("  The same silence.")
    print("  Changed by what")
    print("  filled it.")
