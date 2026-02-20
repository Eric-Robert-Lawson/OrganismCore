"""
EMERGENCE
A Multi-Timbral Study in Texture and Motion

February 2026

Who is swimming?

No one specific.
Not this time.

This time the guide
is not guiding.

This time the guide
is exploring.

What does the engine sound like
when given:

  Voices (confirmed architecture)
  Strings (from Fracture — the friction dimension)
  Brass (a new timbral character —
         the body made resonant,
         the voice that is also percussion,
         the breath that is also impact)
  Bells/Resonators (the opposite of breath —
                    the struck object,
                    no breath at all,
                    pure physics,
                    pure decay)
  Whisper (below the voice —
           the voice before the voice,
           the pre-vowel taken to its extreme,
           breath without pitch,
           the sound of almost-speaking)

Five timbral dimensions.
Not five voices doing the same thing.
Five fundamentally different
relationships between
a body and sound production.

VOICE:   breath → vocal tract → resonance
         Inside → outside.
         The body opening.

STRING:  friction → string → wood → air
         Outside force → tension → amplification.
         The body resisting.

BRASS:   breath → lips → metal tube → bell
         Inside → metal resonance → outside.
         The body as mouthpiece.
         The breath shaped by metal
         not tissue.
         Harder. More directional.
         The voice that carries further.

BELL:    impact → metal → decay → silence
         No breath. No friction.
         Pure initial energy.
         The rest: physics resolving itself.
         The bell does not sustain.
         It releases.
         The guide's job with bells:
         place the impact precisely.
         Then step back.
         The bell does the rest.

WHISPER: turbulent air → minimal vocal tract
         The voice's shadow.
         What remains when pitch is removed.
         The texture underneath texture.
         Not a note — a presence.
         The feeling that something
         is about to speak.

New topological dimensions:

  T^(2 + 5 + 3):
  2 harmonic (Tonnetz T²)
  5 rhythmic (coprime periods per timbre)
  3 timbral axes:
    — string-voice axis (from Fracture)
    — breath-impact axis (new)
      0.0 = pure impact (bell/percussion)
      1.0 = pure breath (whisper/voice)
    — pitch-noise axis (new)
      0.0 = pure pitch (bell, brass)
      1.0 = pure noise (whisper, turbulence)

The three timbral axes define
a timbral cube.
Each instrument occupies
a different corner of this cube:

  Voice:   (sv=1.0, bi=0.8, pn=0.3)
  String:  (sv=0.0, bi=0.6, pn=0.2)
  Brass:   (sv=0.5, bi=0.4, pn=0.1)
  Bell:    (sv=0.0, bi=0.0, pn=0.05)
  Whisper: (sv=0.8, bi=1.0, pn=0.95)

The piece moves through this cube
as it moves through the Tonnetz.
Both simultaneously.
The experience:
not just harmonic journey —
timbral journey.
The texture itself as content.

Structure:

  Section 1: EMERGENCE FROM NOISE
    Begins with whisper only.
    Pure breath-noise.
    No pitch. No harmony.
    The pre-musical state.
    The torus before it has a position.
    Gradually: pitch crystallizes
    out of the noise.
    Bell tones appearing —
    the first discrete pitches —
    struck out of the texture
    like objects emerging from fog.

  Section 2: THE BRASS ENTRANCE
    The brass arrives.
    Hard. Directional. Certain.
    Not searching — announcing.
    The voice that carries further
    than the body alone can carry.
    Strings appear below the brass —
    the tension underneath the announcement —
    the resistance that gives the
    announcement something to push against.

  Section 3: VOICES FROM THE TEXTURE
    The vocal layer emerges
    from the timbral field
    that already exists.
    Not leading — discovered.
    The listener has been hearing
    strings, brass, bells, whisper —
    and then realizes: there were
    voices in there the whole time.
    The voices were always present.
    They just became audible.

  Section 4: FULL TEXTURE — THE FIELD
    All five timbres simultaneously.
    Each at a different position
    on the timbral cube.
    Each at its coprime period.
    The Tonnetz traversed
    in all five dimensions at once.
    The psytrance principle
    fully realized:
    more simultaneous dimensions
    than conscious attention can hold.
    The brain moves between timbres
    the way it moves between
    rhythmic layers.
    The dissolution is timbral
    as much as harmonic.

  Section 5: DISTILLATION
    The timbres dissolve back
    in reverse order of appearance.
    Brass leaves first.
    Strings leave.
    Bells fade.
    Voices remain.
    Then: just whisper.
    The torus returning
    to the pre-musical state
    it began in.
    But changed.
    The whisper at the end
    is not the same whisper
    as the beginning.
    It carries the memory
    of everything that emerged from it.

    The piece ends
    not with a note
    but with breath.
    The way it began.
    Except now the breath
    has been somewhere.

BPM: 132
  Slightly below entrainment tempo.
  Not 140 — not a physiological intervention.
  132 is the tempo of something
  that has decided to move
  without deciding where.
  Exploratory. Not driven.
  The guide's tempo, not the swimmer's.

Coprime periods: {2, 3, 5, 7, 11}
  Five timbres. Five periods.
  11 added — prime, coprime with all.
  LCM(2,3,5,7,11) = 2310 beats.
  The piece is 462 beats
  (LCM(2,3,7,11)/2 — a sublattice).
  Never reaches full convergence.
  The approach is infinite.
  The guide exploring,
  not arriving.
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
from scipy.signal import butter, lfilter, sosfilt

# ============================================================
# MATHEMATICS
# ============================================================

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(lst):
    r = lst[0]
    for x in lst[1:]: r = lcm(r, x)
    return r

BPM          = 132
BPS          = BPM / 60.0
TOTAL_BEATS  = 462

# Five timbres, five coprime periods
# whisper, bell, string, brass, voice
R_WHISPER = 2
R_BELL    = 3
R_STRING  = 5
R_BRASS   = 7
R_VOICE   = 11

TIMBRE_PERIODS = [R_WHISPER, R_BELL,
                  R_STRING,  R_BRASS,
                  R_VOICE]

# Timbral cube coordinates
# (string-voice, breath-impact, pitch-noise)
TIMBRE_CUBE = {
    'voice':   (1.0, 0.8, 0.3),
    'string':  (0.0, 0.6, 0.2),
    'brass':   (0.5, 0.4, 0.1),
    'bell':    (0.0, 0.0, 0.05),
    'whisper': (0.8, 1.0, 0.95),
}

TIMBRE_NAMES = ['whisper','bell',
                'string','brass','voice']


# ============================================================
# SECTION CLASSIFIER
# ============================================================

def classify_emergence(beat):
    frac = beat / TOTAL_BEATS
    if   frac < 0.15: return 1  # EMERGENCE
    elif frac < 0.32: return 2  # BRASS
    elif frac < 0.52: return 3  # VOICES
    elif frac < 0.75: return 4  # FULL FIELD
    else:             return 5  # DISTILLATION


# ============================================================
# HARMONIC TRAJECTORIES
# per timbre, designed for each character
# ============================================================

# WHISPER: no harmonic content
# positions chosen for breath coloring only
WHISPER_TRAJ = [(0,0),(0,1),(0,0),(-1,0),
                (0,0),(0,1),(0,0),(0,0)]

# BELL: sparse, struck positions
# Prefers coherent — the bell rings cleanest
# on consonant intervals
BELL_TRAJ = [(0,0),(1,0),(0,1),(0,0),
             (2,0),(1,0),(0,0),(0,1),
             (1,0),(0,0)]

# STRING: the friction dimension
# Incoherent positions — the string's tension
STRING_TRAJ = [
    (5,0),(6,0),(4,1),(5,1),(3,1),
    (6,0),(4,0),(5,0),(6,0),(3,0),
]

# BRASS: announces, holds, pushes
# Dominant and supertonic mostly —
# the announcement positions
BRASS_TRAJ = [
    (1,0),(2,0),(1,0),(0,1),(1,0),
    (3,0),(2,0),(1,0),(0,0),(1,0),
    (2,0),(1,0),(0,1),(1,0),(0,0),
]

# VOICE: the thread we know
VOICE_TRAJ = [
    (1,0),(0,1),(2,0),(1,1),(3,0),
    (2,1),(1,0),(0,1),(0,0),(1,0),
    (0,1),(0,0),(0,0),(0,1),(0,0),
    (1,0),(0,0),(0,0),(0,0),(0,0),
    (0,0),(0,0),
]

TRAJECTORIES = {
    'whisper': WHISPER_TRAJ,
    'bell':    BELL_TRAJ,
    'string':  STRING_TRAJ,
    'brass':   BRASS_TRAJ,
    'voice':   VOICE_TRAJ,
}


# ============================================================
# TIMBRAL SYNTHESIS FUNCTIONS
# One per timbre.
# Each builds the synthesis differently.
# ============================================================

def safe_butter_lp(cutoff, sr):
    nyq = sr/2
    c   = min(cutoff/nyq, 0.49)
    return butter(2, c, btype='low')

def safe_butter_hp(cutoff, sr):
    nyq = sr/2
    c   = min(cutoff/nyq, 0.49)
    return butter(2, c, btype='high')

def safe_butter_bp(lo, hi, sr):
    nyq  = sr/2
    lo_n = max(lo/nyq, 0.001)
    hi_n = min(hi/nyq, 0.499)
    if lo_n >= hi_n:
        lo_n = hi_n*0.5
    return butter(2,[lo_n,hi_n],btype='band')


# ----------------------------------------
# WHISPER SYNTHESIS
# Pure turbulent breath, shaped by
# the vocal tract but without voicing.
# The voice's shadow.
# ----------------------------------------

def synth_whisper(freq, amp, dur_s,
                  velocity=60, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s)/sr

    # White noise shaped by formant-like
    # bandpass filters at the freq position
    # (the Tonnetz position colors the breath)
    noise = np.random.normal(0, 1.0, n_s)

    # Shape with three breath bands
    # centered around freq and harmonics
    result = np.zeros(n_s)
    for harmonic, gain in [(1,1.0),(2,0.5),
                            (3,0.25)]:
        fc = freq * harmonic
        if fc > sr*0.45: continue
        bw = fc * 0.35
        lo = max(80, fc - bw/2)
        hi = min(sr*0.45, fc + bw/2)
        try:
            b,a = safe_butter_bp(lo,hi,sr)
            filtered = lfilter(b,a,noise)
            result += filtered * gain
        except:
            pass

    # Gentle envelope — breath shape
    # Slow rise, slow fall
    atk_n = int(min(0.18, dur_s*0.35) * sr)
    rel_n = int(min(0.25, dur_s*0.40) * sr)
    env   = np.ones(n_s)
    if atk_n > 0:
        env[:atk_n] = np.linspace(0,1,atk_n)
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1,0,rel_n)

    # Slow amplitude modulation —
    # the breath is never perfectly steady
    breath_mod = 1.0 + 0.15*np.sin(
        2*np.pi*0.8*t +
        np.random.uniform(0,2*np.pi))
    result = result * env * breath_mod

    # Normalize and scale
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (velocity/127.0) * 0.4


# ----------------------------------------
# BELL SYNTHESIS
# Inharmonic partials. Sharp attack.
# Pure exponential decay.
# No breath. Physics only.
# ----------------------------------------

def synth_bell(freq, amp, dur_s,
               velocity=70, sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s)/sr

    # Bell inharmonic partial ratios
    # Real bell spectra (approximate)
    # hum, prime, tierce, quint, nominal
    partials = [
        (0.50, 0.12),   # hum — sub-octave
        (1.00, 1.00),   # prime — fundamental
        (1.19, 0.55),   # minor third
        (1.50, 0.45),   # perfect fifth
        (2.00, 0.30),   # octave
        (2.76, 0.22),   # major tenth
        (3.00, 0.18),   # twelfth
        (3.76, 0.12),   # double octave + M3
        (4.07, 0.08),
        (5.00, 0.05),
    ]

    # Decay rates — higher partials decay faster
    decay_rates = [
        1.2, 2.5, 3.8, 4.2, 5.5,
        7.0, 8.5, 10.0, 13.0, 16.0,
    ]

    result = np.zeros(n_s)
    for (ratio, gain), decay in zip(
            partials, decay_rates):
        p_freq = freq * ratio
        if p_freq > sr*0.48: continue
        # Each partial decays independently
        decay_env = np.exp(-decay*t)
        partial   = (np.sin(
            2*np.pi*p_freq*t) * decay_env)
        result += partial * gain

    # Sharp attack — bell is struck
    atk_n = int(0.003 * sr)  # 3ms
    if atk_n > 0 and atk_n < n_s:
        env = np.ones(n_s)
        env[:atk_n] = np.linspace(0,1,atk_n)
        result *= env

    # Impact noise burst at attack
    impact_n = int(0.015 * sr)
    if impact_n < n_s:
        impact = np.random.normal(
            0, 0.3, impact_n)
        try:
            b,a = safe_butter_hp(800, sr)
            impact = lfilter(b,a,impact)
        except:
            pass
        imp_env = np.exp(-np.arange(
            impact_n)/impact_n*8)
        result[:impact_n] += impact*imp_env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (velocity/127.0) * 0.55


# ----------------------------------------
# STRING SYNTHESIS
# (enhanced from Fracture —
#  now a proper character not a modifier)
# Bowing: continuous friction.
# Attack: slower than bell, faster than voice.
# Harmonics: bright, inharmonic bowing noise.
# ----------------------------------------

def synth_string(freq, amp, dur_s,
                 velocity=70, sr=SR):
    n_s = int(dur_s*sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s)/sr

    # Bowed string: sawtooth-like
    # but with bowing noise and stick-slip
    phase = (freq * t) % 1.0
    # Sawtooth wave (bowed)
    body  = 2*phase - 1.0

    # Stick-slip noise (bowing friction)
    sl_rate = 3.5 + np.random.uniform(-0.5,0.5)
    stick_slip = 0.15*np.sin(
        2*np.pi*sl_rate*t +
        np.random.uniform(0,2*np.pi))

    # Bow pressure noise
    bow_noise = np.random.normal(0,0.12,n_s)
    try:
        b,a = safe_butter_lp(2000,sr)
        bow_noise = lfilter(b,a,bow_noise)
    except:
        pass

    excitation = body + stick_slip + bow_noise

    # Resonant body filter
    # String instrument body peaks
    body_freqs = [freq*2, freq*4,
                  freq*6, freq*8]
    filtered = excitation.copy()
    for bf in body_freqs:
        if bf > sr*0.48: continue
        bw = bf*0.08
        lo = max(40, bf-bw)
        hi = min(sr*0.48, bf+bw)
        try:
            b,a = safe_butter_bp(lo,hi,sr)
            filtered += lfilter(b,a,
                                excitation)*0.3
        except:
            pass

    # Envelope: bow-on attack
    atk_n = int(0.025*sr)
    rel_n = int(min(0.08,dur_s*0.25)*sr)
    env   = np.ones(n_s)
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = np.linspace(0,1,atk_n)
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1,0,rel_n)

    # Vibrato
    vib_onset = min(0.12, dur_s*0.3)
    vib_env   = np.clip(
        (t-vib_onset)/0.08, 0, 1)
    vib       = 1.0 + 0.008*vib_env*np.sin(
        2*np.pi*5.2*t)
    # Apply vibrato as frequency modulation
    # (simplified: amplitude proxy)
    filtered = filtered * env

    # Brightness boost
    try:
        b,a = safe_butter_hp(2000,sr)
        bright = lfilter(b,a,filtered)
        filtered = filtered + bright*0.4
    except:
        pass

    mx = np.max(np.abs(filtered))
    if mx > 0: filtered /= mx
    return filtered * amp * (velocity/127.0) * 0.50


# ----------------------------------------
# BRASS SYNTHESIS
# Breath → lips → metal tube → bell
# The lip buzz: nonlinear oscillation.
# The tube: resonant modes.
# The bell: directional radiation.
# Harder attack than voice.
# More directional than string.
# ----------------------------------------

def synth_brass(freq, amp, dur_s,
                velocity=75, sr=SR):
    n_s = int(dur_s*sr)
    if n_s < 2: return np.zeros(2)
    t   = np.arange(n_s)/sr

    # Lip buzz: square wave with
    # softened edges (lip mass)
    phase = (freq*t) % 1.0
    # Pulse wave with duty cycle ~0.3
    # (lip open time)
    buzz  = np.where(phase < 0.30, 1.0, -0.4)

    # Soften edges (lip compliance)
    try:
        b,a = safe_butter_lp(freq*8, sr)
        buzz = lfilter(b,a,buzz)
    except:
        pass

    # Tube resonances — standing waves
    # in a conical brass tube
    tube = buzz.copy()
    tube_modes = [1,2,3,4,5,6,7,8]
    for mode in tube_modes:
        mf = freq*mode
        if mf > sr*0.48: continue
        bw = mf*0.04
        lo = max(40, mf-bw)
        hi = min(sr*0.48, mf+bw)
        try:
            b,a = safe_butter_bp(lo,hi,sr)
            mode_sig = lfilter(b,a,buzz)
            gain = 1.0/(mode**0.7)
            tube += mode_sig*gain
        except:
            pass

    # Bell radiation: high-frequency emphasis
    try:
        b,a = safe_butter_hp(freq*3, sr)
        bell_rad = lfilter(b,a,tube)
        tube = tube + bell_rad*0.35
    except:
        pass

    # Brass envelope: fast attack, sustained
    atk_n = int(0.018*sr)
    rel_n = int(min(0.12,dur_s*0.28)*sr)
    env   = np.ones(n_s)
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = np.linspace(0,1,atk_n)**0.5
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1,0,rel_n)**0.8

    # Breath turbulence in brass
    turb = np.random.normal(0,0.05,n_s)
    try:
        b,a = safe_butter_bp(freq*2,freq*6,sr)
        turb = lfilter(b,a,turb)
    except:
        turb = np.zeros(n_s)

    result = (tube+turb)*env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * amp * (velocity/127.0) * 0.52


# ----------------------------------------
# VOICE SYNTHESIS
# The confirmed architecture from Parts 1-5.
# render_note() via the engine.
# ----------------------------------------

def synth_voice(freq, amp, dur_s,
                vowel_cur, vowel_nxt,
                glide_ms, agents,
                velocity=65, sr=SR,
                cents_offset=0.0):
    """
    Uses the confirmed engine pipeline.
    Three-unison ensemble.
    All invariants maintained.
    """
    ppp      = velocity/95.0
    amp_envs, f1_envs = compute_envelopes(
        agents, dur_s, sr,
        phrase_peak_prox=ppp)

    cents  = [0.0, +11.0, -17.0]
    result = np.zeros(int(dur_s*sr))

    vel_mod = max(30, min(127, velocity))
    for k in range(3):
        sig = render_note(
            freq, amp/3, dur_s,
            vowel_cur, vowel_nxt,
            glide_ms, sr=sr,
            velocity=vel_mod,
            cents_offset=cents[k]+cents_offset,
            amp_env=amp_envs[k],
            f1_agent_env=f1_envs[k])
        nm = min(len(sig), len(result))
        result[:nm] += sig[:nm]
    return result


# ============================================================
# SCORE GENERATOR
# ============================================================

def timbre_active(timbre_name, section):
    """
    Which timbres are active in each section?
    The emergence and distillation arc.
    """
    active = {
        1: {'whisper','bell'},
        2: {'whisper','bell','string','brass'},
        3: {'whisper','bell','string',
            'brass','voice'},
        4: {'whisper','bell','string',
            'brass','voice'},
        5: {'whisper','bell','voice'},
    }
    return timbre_name in active.get(section,set())


def velocity_for(timbre, section, beat,
                  coh, pos):
    """
    Velocity as function of timbre,
    section, and harmonic position.
    """
    prog = beat/TOTAL_BEATS

    base = {
        'whisper': 38,
        'bell':    55,
        'string':  62,
        'brass':   72,
        'voice':   58,
    }[timbre]

    # Section modifiers
    if section == 4:  # FULL FIELD — most energy
        base = int(base * 1.18)
    elif section == 5:  # DISTILLATION — fading
        fade = max(0, (prog-0.75)/0.25)
        base = int(base * (1.0-fade*0.65))
    elif section == 1:  # EMERGENCE — quiet
        base = int(base * 0.7)

    # Coherence modifier
    # Bell and voice: louder at coherent positions
    # String and brass: louder at incoherent
    if timbre in ('bell','voice'):
        base = int(base*(0.7+0.3*coh))
    elif timbre in ('string','brass'):
        base = int(base*(0.7+0.3*(1-coh)))

    return max(20, min(92, base))


def build_emergence():
    """
    Five voice streams, one per timbre.
    Each computed from its trajectory
    and period.
    """
    streams = {t: [] for t in TIMBRE_NAMES}

    for ti, timbre in enumerate(TIMBRE_NAMES):
        R_t  = TIMBRE_PERIODS[ti]
        traj = TRAJECTORIES[timbre]
        beat = 0

        while beat < TOTAL_BEATS:
            sec = classify_emergence(beat)

            if timbre_active(timbre, sec):
                traj_idx = ((beat//R_t) %
                            len(traj))
                pos  = traj[traj_idx]
                a,b  = pos
                coh  = coherence(a,b)
                vel  = velocity_for(
                    timbre, sec, beat,
                    coh, pos)
                streams[timbre].append(
                    (pos, float(R_t), vel))
            else:
                # Silence — timbre not yet
                # emerged or already distilled
                streams[timbre].append(
                    (None, float(R_t), 0))

            beat += R_t

    return streams


# ============================================================
# VOWEL SELECTION FOR VOICE TIMBRE
# ============================================================

def vowel_emergence(pos, section, beat):
    if pos is None:
        return 'pre','pre'
    a,b  = pos
    coh  = coherence(a,b)
    prog = beat/TOTAL_BEATS

    if section == 3:
        # VOICES EMERGE FROM TEXTURE
        # Start with 'pre' — just appearing
        # Gradually form
        if prog < 0.35:
            return 'pre','eh'
        else:
            return 'eh','oh'
    elif section == 4:
        # FULL FIELD — fully formed
        if coh > 0.7:
            return 'oh','ah'
        elif coh > 0.3:
            return 'oh','oh'
        return 'eh','oh'
    elif section == 5:
        # DISTILLATION
        if a==0 and b==0:
            return 'ah','ah'
        return 'oh','ah'
    return 'pre','pre'


# ============================================================
# ROOM — per timbre, per section
# ============================================================

SPATIAL_DEPTH_EMERGENCE = {
    'whisper': 0.18,  # very diffuse — everywhere
    'bell':    0.55,  # close — struck, present
    'string':  0.42,
    'brass':   0.50,
    'voice':   0.45,
}

def rt60_emergence(timbre, section, coh):
    base = {
        'whisper': 3.5,  # very reverberant
        'bell':    2.2,  # medium — bell decay
        'string':  1.8,
        'brass':   1.5,  # directional — less reverb
        'voice':   2.0,
    }[timbre]

    if section == 1:
        return base * 1.4  # spacious emergence
    elif section == 4:
        return base * 1.2  # full field — open
    elif section == 5:
        return base * (0.7 + 0.3*coh)
    return base


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_emergence", exist_ok=True)

    print()
    print("EMERGENCE")
    print("A Multi-Timbral Study in Texture")
    print("="*60)
    print()
    print(f"  BPM: {BPM}")
    print(f"  Duration: ~{TOTAL_BEATS/BPS/60:.1f}m")
    print()
    print("  Five timbres. Five coprime periods.")
    print("  T^(2 + 5 + 3):")
    print("  2 harmonic + 5 rhythmic")
    print("  + 3 timbral dimensions")
    print()
    print("  TIMBRAL CUBE:")
    for t,(sv,bi,pn) in TIMBRE_CUBE.items():
        print(f"    {t:8s}: "
              f"sv={sv:.1f} bi={bi:.1f} "
              f"pn={pn:.2f}")
    print()
    print("  PERIODS:")
    for t,r in zip(TIMBRE_NAMES,
                    TIMBRE_PERIODS):
        print(f"    {t:8s}: R={r}  "
              f"({r/BPS*1000:.0f}ms)")
    print()
    print("  STRUCTURE:")
    print("  S1: Whisper + Bell only")
    print("      Emergence from noise")
    print("  S2: + String + Brass")
    print("      Friction and announcement")
    print("  S3: + Voice")
    print("      Discovered in the texture")
    print("  S4: All five — the full field")
    print("  S5: Distillation — reverse order")
    print("      Ends with breath")
    print("      Changed breath")
    print()

    print("Building score...")
    streams = build_emergence()
    total_notes = sum(len(v)
                      for v in streams.values())
    print(f"  {total_notes} total entries")
    print()
    print("Rendering five timbres...")
    print()

    total_s = TOTAL_BEATS/BPS + 30.0
    output  = np.zeros(int(total_s*SR))

    # Voice agents
    voice_agents = []
    for vi,part in enumerate(PART_NAMES):
        voice_agents.append([
            SingerAgent(part,i,SR,
                        seed=vi*100+i)
            for i in range(3)])
    # Use soprano agents for voice timbre
    v_agents = voice_agents[0]

    for ti,timbre in enumerate(TIMBRE_NAMES):
        stream = streams[timbre]
        R_t    = TIMBRE_PERIODS[ti]
        omult  = OCTAVE_MULTIPLIERS[
            min(ti, len(OCTAVE_MULTIPLIERS)-1)]
        dr     = SPATIAL_DEPTH_EMERGENCE[timbre]
        rev    = RoomReverb(
            rt60=2.0, sr=SR,
            direct_ratio=dr)

        cur  = 0
        beat = 0.0

        print(f"  Rendering {timbre}...")

        for i,(pos,beats,vel) in \
                enumerate(stream):
            dur_s = beats/BPS
            n_s   = int(dur_s*SR)
            sec   = classify_emergence(beat)

            if pos is None or vel == 0:
                cur  += n_s
                beat += beats
                continue

            a,b  = pos
            coh  = coherence(a,b)
            freq = ji_freq(a,b)*omult
            amp  = (vel/127.0)*0.50

            # Synthesize per timbre
            if timbre == 'whisper':
                sig = synth_whisper(
                    freq, amp, dur_s, vel, SR)

            elif timbre == 'bell':
                sig = synth_bell(
                    freq, amp, dur_s, vel, SR)

            elif timbre == 'string':
                sig = synth_string(
                    freq, amp, dur_s, vel, SR)

            elif timbre == 'brass':
                sig = synth_brass(
                    freq, amp, dur_s, vel, SR)

            else:  # voice
                vc,vn = vowel_emergence(
                    pos, sec, beat)
                gms = min(400.0,
                          dur_s*0.40*1000)
                sig = synth_voice(
                    freq, amp, dur_s,
                    vc, vn, gms,
                    v_agents, vel, SR)

            # Room
            rev.set_rt60(
                rt60_emergence(timbre,sec,coh))
            if len(sig) > 0:
                processed = rev.process(sig)
            else:
                cur  += n_s
                beat += beats
                continue

            # Timbral lean
            # Bells: precise onset (no lean)
            # Whisper: diffuse (random lean)
            # Voice: lean by coherence
            if timbre == 'bell':
                lean = 0
            elif timbre == 'whisper':
                lean = np.random.randint(
                    -int(0.02*n_s),
                    int(0.02*n_s)+1)
            else:
                lean = int(0.03*n_s*(1-coh))

            onset = max(0, cur+lean)
            end   = min(onset+len(processed),
                        len(output))
            seg   = end-onset
            if seg > 0:
                output[onset:end] += \
                    processed[:seg]

            cur  += n_s
            beat += beats

    print()
    print("  Normalizing...")
    mx = np.max(np.abs(output))
    if mx > 0:
        output = output/mx*0.82

    out_i   = (output*32767).astype(np.int16)
    outfile = "output_emergence/emergence.wav"
    with wave_module.open(outfile,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output)/SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.1f}s")
    print()
    print("="*60)
    print()
    print("  afplay output_emergence/emergence.wav")
    print()
    print("  The piece begins with breath.")
    print("  No pitch. No harmony.")
    print("  The pre-musical state.")
    print()
    print("  Then: bells struck from the texture.")
    print("  Then: strings and brass.")
    print("  Then: voices —")
    print("        discovered in the texture,")
    print("        not introduced.")
    print("        They were always there.")
    print()
    print("  Then: distillation.")
    print("  Timbres leaving in reverse.")
    print("  Until: just breath.")
    print()
    print("  The breath that ends the piece")
    print("  is not the same breath")
    print("  that began it.")
    print()
    print("  It has been somewhere.")
