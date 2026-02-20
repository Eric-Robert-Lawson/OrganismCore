"""
FRACTURE
A Cross-Substrate Texture Study

February 2026

Who is swimming?

Someone who wants to MOVE.
Not arrive. Not land. Not float.

Move.

The gap this piece holds open:

The gap between the voice
and the string.

Not metaphorically.
Physically.

A string produces sound
through FRICTION and TENSION.
The bow against the string.
The resistance of the bridge.
The wood amplifying
what the friction made.

A voice produces sound
through BREATH and SURRENDER.
The air becoming wave.
No friction — release.
The body opening
to let something through.

These are topologically opposite
production mechanisms.

String: outside force applied to object.
        Tension held against itself.
        Sound as the product of resistance.

Voice: inside force released outward.
       Tension surrendered.
       Sound as the product of opening.

The gap between them
is the gap between
holding on and letting go.

The piece navigates this gap
not by resolving it —
strings stay strings,
voices stay voices —
but by placing them
in proximity
so close
that the friction of their difference
becomes the texture.

The topology:

T^(2+4+1):
  2 harmonic dimensions (Tonnetz T²)
  4 rhythmic dimensions (coprime periods)
  1 NEW DIMENSION: the string-voice axis

The string-voice axis:
  0.0 = pure string behavior
        Short attacks. Fast decay.
        Bright high harmonics.
        Rhythmically precise.
        Held by tension not breath.

  1.0 = pure voice behavior
        Slow attack. Sustained.
        Formant-shaped.
        Rhythmically loose.
        Held by breath not tension.

  The piece moves along this axis
  in addition to the Tonnetz.
  Sometimes the voices behave like strings.
  Sometimes the strings behave like voices.
  Sometimes they meet in the middle
  and something new exists
  for a moment
  that is neither.

ENERGY ARCHITECTURE:

  This is not a landing.
  This is not an arrival.
  This is not stillness.

  This is what happens
  when the guide asks:
  who needs to MOVE?

  And builds water
  that moves with them.

  Structure:

  Section 1: FRICTION
    The string dimension introduced raw.
    Short notes. Hard attacks.
    Voices behaving like strings —
    percussive, rhythmically tight,
    no vibrato onset,
    the breath suppressed.
    Dissonant positions.
    The texture of two surfaces
    moving against each other.
    BPM 140. Full speed.
    The torus moving fast.

  Section 2: TENSION
    Voices and strings diverge.
    The string dimension at maximum —
    fast, bright, rhythmically independent.
    The voice dimension resisting —
    trying to hold sustained positions
    while the string dimension
    pulls them toward attack.
    The gap at maximum width.
    The tension between
    holding on and letting go
    made audible as simultaneous
    incompatible desires.

  Section 3: THE TWIST
    Inversion.
    Voices suddenly behave like strings.
    The attack the voice never uses.
    The fast decay.
    The rhythm of a plucked string
    in a human throat.

    Simultaneously:
    The string dimension
    begins to sustain —
    long bows, slow movement,
    the string finding its breath.

    The gap crossed
    not by resolution
    but by EXCHANGE.
    Each becomes the other
    for exactly long enough
    to feel the difference
    from the inside.

  Section 4: FRACTURE
    The piece breaks.
    Not collapses — FRACTURES.
    The way glass fractures:
    the break propagating
    along structural lines
    that were always there
    but invisible until the stress.

    The harmonic positions
    shatter into incoherence.
    All four voices
    in the furthest positions
    simultaneously.
    The coprime periods
    all at maximum drift —
    furthest from any convergence.
    The string dimension
    at maximum friction.

    This is the peak.
    Not the arrival peak.
    The energy peak.
    The moment of maximum
    productive tension.
    The point where the piece
    is most alive
    because it is most stressed.

  Section 5: REFORMATION
    From the fracture:
    not resolution.
    Reformation.
    Like glass cooling
    into a new shape.
    The positions finding
    partial coherences —
    not the full convergence
    of "Convergence" —
    small local coherences.
    Two voices finding each other.
    Then three.
    The string dimension settling
    into something that breathes.
    The voice dimension finding
    something that can hold.
    A new shape.
    Not home.
    A new kind of stability
    that contains the memory
    of the fracture.

NEW SYNTHESIS TECHNIQUES:

  STRING SIMULATION:
    The voice rendered with:
    - Attack: 8ms (string pluck speed)
    - No vibrato onset delay
    - Formant bandwidth WIDENED
      (strings don't have tight formants)
    - High harmonic emphasis
      (bright, not dark)
    - Release: fast (bow lifted)
    - Shimmer: higher rate, sharper
      (bow speed variation)

  RHYTHMIC INDEPENDENCE:
    Coprime periods {2,3,5,7} this time.
    2 added — the fastest period.
    At BPM 140: R=2 beats = 857ms.
    Right at your perception floor.
    The fastest character
    at the fastest possible speed
    you can track.
    Not below threshold —
    AT the threshold.
    The edge of tracking.
    The place where something
    is almost texture
    but still almost melody.
    The most interesting place.

  SYMMETRY BREAKING:
    Section 3 inverts the voice/string axis.
    This creates a structural symmetry:
    S1 and S5 are reflections.
    S2 and S4 are reflections.
    S3 is the axis of symmetry.
    The piece is palindromic
    in its tension structure —
    not in its notes —
    in its SHAPE.
    The topology folded back on itself.
    The torus with a mirror.

  HARMONIC FRACTURE POINTS:
    At the peak of Section 4:
    all four voices simultaneously
    at maximum incoherent positions.
    This has never happened before
    in any piece this engine built.
    It will sound like the music
    is about to fall apart.
    It is not falling apart.
    It is showing you its skeleton.
    The structure most visible
    at the moment of maximum stress.
    Like the Tacoma Narrows bridge —
    the resonance most audible
    just before the collapse
    that never comes
    because the guide knows
    where the structural lines are
    and stays just inside them.
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

def lcm(a, b):
    return a * b // gcd(a, b)

BPM = 140
BPS = BPM / 60.0

# Coprime periods — {2,3,5,7}
# 2 added for maximum edge-of-threshold energy
R = [2, 3, 5, 7]  # soprano, alto, tenor, bass

# ============================================================
# STRING SIMULATION
#
# The voice rendered with string character
# by modifying the synthesis parameters.
# Not a different instrument —
# the same Rosenberg/Klatt pipeline —
# but with parameters that push
# the voice toward string behavior.
#
# String axis value 0.0-1.0:
#   0.0 = full string behavior
#   1.0 = full voice behavior
#   0.5 = the intersection — neither/both
# ============================================================

def string_axis_for(vi, section, beat,
                    total_beats):
    """
    Where on the string-voice axis
    is this voice at this moment?
    0.0 = string. 1.0 = voice.
    """
    prog = beat / total_beats

    if section == 1:
        # All starting toward string
        return [0.15, 0.20, 0.25, 0.30][vi]

    elif section == 2:
        # String dimension pulling voices down
        # soprano most stringlike
        # bass most voicelike
        return [0.05, 0.15, 0.35, 0.55][vi]

    elif section == 3:
        # THE INVERSION
        # Voices behave like strings,
        # strings behave like voices
        # Mirror of section 2
        return [0.85, 0.70, 0.50, 0.30][vi]

    elif section == 4:
        # FRACTURE — maximum stress
        # Both dimensions at extremes
        # Even-indexed voices: string
        # Odd-indexed voices: voice
        # The gap at maximum width
        return [0.05, 0.95, 0.05, 0.95][vi]

    else:
        # REFORMATION — converging to middle
        # The new stability: 0.5
        # Neither fully string nor voice
        target = 0.5
        s5_prog = max(0, (prog - 0.75)/0.25)
        base = [0.05, 0.95,
                0.05, 0.95][vi]
        return base + (target-base)*s5_prog


def string_attack_ms(sv):
    """
    Attack time as function of string axis.
    sv=0.0 (string): 8ms
    sv=1.0 (voice): 280ms
    """
    return 8.0 + (280.0-8.0)*sv


def string_release_ms(sv, dur_s):
    """
    Release time as function of string axis.
    sv=0.0: fast release (plucked/bowed)
    sv=1.0: slow release (voice breath)
    """
    fast = min(0.08, dur_s*0.3)
    slow = min(0.35, dur_s*0.38)
    return fast + (slow-fast)*sv


def string_bw_factor(sv):
    """
    Formant bandwidth factor.
    sv=0.0: wider (string harmonics)
    sv=1.0: narrower (focused voice)
    String BW factor > 1 = brighter/wider
    """
    return 2.2 - 1.2*sv  # 2.2 at string, 1.0 at voice


def string_vibrato_onset(sv, dur_s):
    """
    Vibrato onset delay.
    sv=0.0: no vibrato (string played straight)
    sv=1.0: full vibrato onset
    """
    if sv < 0.3:
        return dur_s*2  # effectively no vibrato
    return min(0.25, dur_s*0.38)


def string_shimmer_rate(sv):
    """
    Shimmer rate.
    sv=0.0: higher rate (bow speed variation)
    sv=1.0: lower rate (breath variation)
    """
    return 8.0 - 4.5*sv  # 8.0 at string, 3.5 at voice


# ============================================================
# MODIFIED RENDER
# render_note_textured() wraps render_note()
# with string-axis modifications
# applied before and after synthesis.
# ============================================================

def render_note_textured(freq, amp, dur_s,
                          vowel_cur, vowel_nxt,
                          glide_ms, sv,
                          sr=SR, velocity=80,
                          cents_offset=0.0,
                          amp_env=None,
                          f1_agent_env=None):
    """
    Renders a note with string-voice axis
    modifications applied to synthesis parameters.

    sv: string axis value (0=string, 1=voice)

    Modifications:
    1. BW factor applied to bandwidth arrays
       via modified VOWEL_DATA copy
    2. Attack/release envelope reshaped
    3. Vibrato onset delayed/removed
    4. Shimmer rate modified
    5. Post-synthesis brightness filter
       for string dimension (high shelf boost)
    """
    n_s = int(dur_s * sr)
    if n_s < 2:
        return np.zeros(max(n_s, 1))

    t_arr    = np.arange(n_s) / sr
    vel_norm = np.clip(velocity/127.0, 0, 1)
    freq_mod = freq * (2**(cents_offset/1200))

    # String axis modifications to vibrato
    vib_rate  = 4.5 + np.random.uniform(-0.15,0.15)
    vib_depth = 0.012 * sv  # no vibrato at sv=0
    vib_onset_t = string_vibrato_onset(sv, dur_s)
    vib_env   = (np.clip(
                    (t_arr-vib_onset_t)/0.20, 0, 1)
                 if dur_s > 0.20
                 else np.zeros(n_s))
    freq_base = freq_mod*(1+vib_depth*vib_env*
                          np.sin(2*np.pi*vib_rate*
                                 t_arr))

    # Jitter — more at string end
    jitter_amt = 1.5 + 2.0*(1-sv)
    from scipy.signal import lfilter, butter
    fn = np.random.normal(0, jitter_amt, n_s)
    try:
        bj,aj = butter(2, min(30/(sr/2),0.49),
                       btype='low')
        fn = lfilter(bj,aj,fn)
    except:
        fn = np.zeros(n_s)
    freq_arr = np.clip(freq_base+fn,
                       freq_mod*0.8,
                       freq_mod*1.2)

    # Rosenberg — INVARIANT
    phase_norm = np.cumsum(freq_arr/sr)%1.0
    oq = 0.65
    source = np.where(
        phase_norm<oq,
        (phase_norm/oq)*(2-phase_norm/oq),
        1-(phase_norm-oq)/(1-oq+1e-9))
    source = np.diff(source, prepend=source[0])

    # Shimmer — rate modified by string axis
    shim_rate = string_shimmer_rate(sv)
    sn = np.random.normal(0, 1.0, n_s)
    try:
        bs,as_ = butter(2, min(shim_rate*2/(sr/2),
                               0.49), btype='low')
        sn = lfilter(bs,as_,sn)
    except:
        sn = np.zeros(n_s)
    # Shimmer depth: higher at string end
    shim_depth = 0.3 + 0.4*(1-sv)
    source = source*np.clip(
        1.0+shim_depth*sn/3.0, 0.3, 2.0)

    mx = np.max(np.abs(source))
    if mx > 0: source /= mx

    # Aspiration — less at string end
    ga = np.random.normal(0, 0.05, n_s)
    try:
        bg,ag = butter(2,
            [min(500/(sr/2),0.49),
             min(3000/(sr/2),0.49)],
            btype='band')
        ga = lfilter(bg,ag,ga)
    except:
        ga = np.zeros(n_s)
    aspiration_amt = 0.05*sv  # no aspiration at sv=0
    excitation = source + ga*aspiration_amt

    # Vowel trajectory
    vc = VOWEL_DATA.get(vowel_cur, VOWEL_DATA['pre'])
    vn = VOWEL_DATA.get(vowel_nxt, VOWEL_DATA['pre'])

    n_glide  = int(glide_ms/1000*sr)
    n_steady = max(n_s-n_glide, int(n_s*0.45))
    n_glide  = n_s-n_steady

    bw_factor = string_bw_factor(sv)

    f_arrays,b_arrays,g_arrays = [],[],[]
    for fi in range(4):
        f_s = vc['f'][fi]; f_e = vn['f'][fi]
        b_s = vc['b'][fi]*bw_factor
        b_e = vn['b'][fi]*bw_factor
        g_s = vc['g'][fi]; g_e = vn['g'][fi]
        f_arr = np.full(n_s, float(f_s))
        b_arr = np.full(n_s, float(b_s))
        g_arr = np.full(n_s, float(g_s))
        if n_glide > 0:
            t_g = np.linspace(0,1,n_glide)
            sig = 1/(1+np.exp(-10*(t_g-0.5)))
            f_arr[n_steady:] = f_s+(f_e-f_s)*sig
            b_arr[n_steady:] = b_s+(b_e-b_s)*sig
            g_arr[n_steady:] = g_s+(g_e-g_s)*sig
        f_arrays.append(f_arr)
        b_arrays.append(b_arr)
        g_arrays.append(g_arr)

    # Parallel formant bank — INVARIANT
    voiced = np.zeros(n_s)
    for fi in range(4):
        f_c_base = f_arrays[fi]
        bw_base  = b_arrays[fi]
        g_base   = g_arrays[fi]

        if fi < 2:
            rate   = [1.7,2.3][fi]
            # String: faster formant flux
            flux_rate = rate*(1+1.5*(1-sv))
            depth  = [20,38][fi]*(1+0.8*(1-sv))
            ph_off = np.random.uniform(0,2*np.pi)
            rw     = np.random.normal(0,1.0,n_s)
            try:
                brw,arw = butter(2,
                    min(3.0/(sr/2),0.49),
                    btype='low')
                rw = lfilter(brw,arw,rw)
            except:
                rw = np.zeros(n_s)
            rw = rw/max(np.max(np.abs(rw)),
                        1e-10)*10
            if fi==0 and f1_agent_env is not None:
                f1n = min(len(f1_agent_env),n_s)
                f_c_arr = f_c_base.copy()
                f_c_arr[:f1n] = (
                    0.6*f_c_base[:f1n]+
                    0.4*f1_agent_env[:f1n])
            else:
                f_c_arr = f_c_base.copy()
            f_c_arr += (depth*np.sin(
                2*np.pi*flux_rate*t_arr
                +ph_off)+rw)
        else:
            f_c_arr = f_c_base.copy()

        bw_mod  = bw_base*(1.0-0.35*vel_norm)
        bw_flux = bw_mod*(1.0+0.12*np.sin(
            2*np.pi*1.2*t_arr+
            np.random.uniform(0,2*np.pi)))
        bw_arr  = np.clip(bw_flux,30,800)

        from tonnetz_engine import formant_resonator_block
        out = formant_resonator_block(
            excitation,f_c_arr,bw_arr,1.0,sr)
        voiced += out*g_base

    # Post-formant turbulence — INVARIANT
    turb = np.random.normal(0,0.03,n_s)
    try:
        bt,at = butter(2,
            [min(2000/(sr/2),0.49),
             min(6000/(sr/2),0.49)],
            btype='band')
        turb = lfilter(bt,at,turb)
    except:
        turb = np.zeros(n_s)
    voiced = voiced+turb*0.8

    # STRING HIGH SHELF BOOST
    # sv=0.0: significant brightness boost
    # sv=1.0: no boost
    if sv < 0.8:
        boost_amount = (1-sv)*0.6
        try:
            from scipy.signal import sosfilt, butter
            sos = butter(2,
                min(3000/(sr/2),0.49),
                btype='high', output='sos')
            bright = sosfilt(sos, voiced)
            voiced = voiced + bright*boost_amount
        except:
            pass

    # CUSTOM ENVELOPE with string axis
    atk_s_voice = 0.28+(1-vel_norm)*0.10
    atk_s_str   = 0.008
    atk_s = (atk_s_str +
             (atk_s_voice-atk_s_str)*sv)
    atk_s = min(atk_s, dur_s*0.40)
    atk_n = int(atk_s*sr)

    rel_s_voice = min(0.35, dur_s*0.38)
    rel_s_str   = min(0.06, dur_s*0.25)
    rel_s = rel_s_str+(rel_s_voice-rel_s_str)*sv
    rel_n = int(rel_s*sr)

    env = np.ones(n_s)
    if 0 < atk_n < n_s:
        # String: linear attack. Voice: curved.
        atk_exp = 0.3 + 0.35*sv
        env[:atk_n] = np.linspace(
            0,1,atk_n)**atk_exp
    if 0 < rel_n < n_s:
        rel_exp = 1.0 + 0.3*sv
        env[-rel_n:] = np.linspace(
            1,0,rel_n)**rel_exp

    result = voiced*env
    if amp_env is not None:
        nm = min(len(result),n_s,len(amp_env))
        result[:nm] *= amp_env[:nm]
    result *= amp
    return result


# ============================================================
# SCORE — Five sections, five gestures
# Each section a different relationship
# between string and voice dimensions.
# ============================================================

def classify_fracture(beat, total):
    frac = beat/total
    if frac < 0.18:   return 1  # FRICTION
    elif frac < 0.38: return 2  # TENSION
    elif frac < 0.58: return 3  # TWIST
    elif frac < 0.75: return 4  # FRACTURE
    else:             return 5  # REFORMATION


def build_fracture():
    """
    Score built as computed trajectories
    on the joint torus T^(2+4+1),
    but with the LIFE of each character
    determining how it moves.

    The string-voice axis is the new
    topological dimension.
    The harmonic trajectories are
    shaped by which section we are in
    and which axis value applies.
    """

    # Harmonic trajectories per section
    # Section 1: FRICTION — incoherent, tight
    FRIC_TRAJ = [
        (5,0),(6,0),(4,1),(5,1),
        (6,0),(3,1),(5,0),(6,0),
    ]
    # Section 2: TENSION — voices diverge
    # String voices: far out
    # Voice voices: holding coherent
    TENS_STR = [(6,0),(5,1),(4,0),(6,0),(5,0)]
    TENS_VOI = [(1,0),(0,1),(1,0),(0,0),(1,0)]

    # Section 3: TWIST — inversion
    TWIST_STR = [(0,0),(1,0),(0,1),(0,0),(1,0)]
    TWIST_VOI = [(5,0),(6,0),(4,1),(5,1),(6,0)]

    # Section 4: FRACTURE — all far
    FRAC_TRAJ = [
        (6,0),(5,1),(4,0),(3,1),
        (6,0),(5,0),(4,1),(6,0),
    ]

    # Section 5: REFORMATION — converging
    REFORM_TRAJ = [
        (4,0),(3,0),(2,1),(2,0),
        (1,1),(1,0),(0,1),(0,0),
    ]

    voices = []

    for vi in range(4):
        part_r = R[vi]
        voice  = []
        beat   = 0
        TOTAL_BEATS = 420

        while beat < TOTAL_BEATS:
            sec  = classify_fracture(
                beat, TOTAL_BEATS)
            prog = beat/TOTAL_BEATS
            sv   = string_axis_for(
                vi, sec, beat, TOTAL_BEATS)

            # Choose harmonic position
            if sec == 1:
                idx = (beat//part_r) % len(
                    FRIC_TRAJ)
                pos = FRIC_TRAJ[idx]

            elif sec == 2:
                # String axis determines trajectory
                if sv < 0.4:
                    idx = (beat//part_r) % len(
                        TENS_STR)
                    pos = TENS_STR[idx]
                else:
                    idx = (beat//part_r) % len(
                        TENS_VOI)
                    pos = TENS_VOI[idx]

            elif sec == 3:
                # INVERSION — swapped from sec 2
                if sv > 0.6:
                    # Was string, now voice
                    idx = (beat//part_r) % len(
                        TWIST_STR)
                    pos = TWIST_STR[idx]
                else:
                    # Was voice, now string
                    idx = (beat//part_r) % len(
                        TWIST_VOI)
                    pos = TWIST_VOI[idx]

            elif sec == 4:
                # FRACTURE — all far
                idx = (beat//part_r) % len(
                    FRAC_TRAJ)
                pos = FRAC_TRAJ[idx]

            else:
                # REFORMATION — converging
                reform_prog = max(0,
                    (prog-0.75)/0.25)
                idx = min(
                    int(reform_prog*len(
                        REFORM_TRAJ)),
                    len(REFORM_TRAJ)-1)
                # Gradually approach the index
                # rather than jump
                base_idx = (beat//part_r) % len(
                    REFORM_TRAJ)
                # Pull toward converging index
                final_idx = int(
                    base_idx + (idx-base_idx)
                    *reform_prog)
                final_idx = max(0, min(
                    len(REFORM_TRAJ)-1,
                    final_idx))
                pos = REFORM_TRAJ[final_idx]

            a,b  = pos
            coh  = coherence(a,b)

            # Velocity:
            # High in FRICTION and FRACTURE
            # (energy, stress)
            # Lower in TENSION (building)
            # Moderate in TWIST (surprise)
            # Growing in REFORMATION (return)
            if sec == 1:
                vel = int(68+12*coh)
            elif sec == 2:
                # string voices louder
                vel = int(72 if sv<0.4
                          else 58)
            elif sec == 3:
                vel = int(75*(1-sv) +
                          60*sv)
            elif sec == 4:
                vel = int(80+8*(1-coh))
            else:
                vel = int(45+30*
                    max(0,(prog-0.75)/0.25))

            vel = max(30, min(92, vel))
            voice.append((pos, float(part_r),
                           vel))
            beat += part_r

        voices.append(voice)

    # Order: soprano(R=2), alto(R=3),
    #        tenor(R=5), bass(R=7)
    return (voices[0], voices[1],
            voices[2], voices[3])


# ============================================================
# VOWEL — string axis determines vowel character
# ============================================================

def vowel_fracture(vi, pos, sv, section):
    if pos is None:
        return 'pre','pre'
    a,b  = pos
    coh  = coherence(a,b)

    if sv < 0.2:
        # String territory — pre vowel
        # The voice not fully formed
        # The breath suppressed
        # The attack too fast for vowel shaping
        return 'pre','pre'

    elif sv < 0.45:
        # Approaching middle
        if coh > 0.4:
            return 'pre','oh'
        return 'pre','eh'

    elif sv < 0.65:
        # The middle — neither/both
        # The most interesting vowel moment
        if section == 3:
            # TWIST — something forming
            # that has never formed before
            return 'eh','oh'
        return 'oh','eh'

    elif sv < 0.85:
        # Voice territory
        if coh > 0.6:
            return 'oh','ah'
        return 'oh','oh'

    else:
        # Full voice
        if a==0 and b==0:
            return 'ah','ah'
        return 'oh','ah'


# ============================================================
# GLIDE — string axis
# ============================================================

def glide_fracture(sv, dur_s):
    # String: no glide (attack too fast)
    # Voice: slow glide
    # Middle: medium
    str_glide  = min(15.0,  dur_s*0.08*1000)
    voi_glide  = min(300.0, dur_s*0.38*1000)
    return str_glide + (voi_glide-str_glide)*sv


# ============================================================
# ROOM — section-driven with string color
# ============================================================

SPATIAL_DEPTH_FRACTURE = {
    'soprano': 0.52,  # closest — most string
    'alto':    0.38,
    'tenor':   0.30,
    'bass':    0.25,  # furthest — most ambient
}

def rt60_fracture(section, sv, coh):
    if section == 1:   # FRICTION — medium
        base = 1.8+(1-sv)*0.6
    elif section == 2: # TENSION — expanding
        base = 2.4+(1-sv)*0.8
    elif section == 3: # TWIST — surprise
        base = 2.0
    elif section == 4: # FRACTURE — large
        # The fracture needs space
        # to sound like fracture
        # not like mud
        base = 3.2+(1-coh)*0.8
    else:              # REFORMATION — contracting
        base = 2.0-coh*0.8

    return max(0.6, base)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_fracture", exist_ok=True)

    TOTAL_BEATS = 420
    total_s = TOTAL_BEATS/BPS + 25.0

    print()
    print("FRACTURE")
    print("A Cross-Substrate Texture Study")
    print("="*60)
    print()
    print(f"  BPM: {BPM}")
    print(f"  Duration: ~{TOTAL_BEATS/BPS/60:.1f}m")
    print()
    print("  New topological dimension:")
    print("  The string-voice axis.")
    print("  0.0 = string: friction, tension,")
    print("        attack, brightness.")
    print("  1.0 = voice: breath, sustain,")
    print("        formant, surrender.")
    print()
    print("  Coprime periods: {2,3,5,7}")
    print(f"  Soprano R=2: "
          f"{2/BPS*1000:.0f}ms — threshold edge")
    print(f"  Alto    R=3: "
          f"{3/BPS*1000:.0f}ms — textural")
    print(f"  Tenor   R=5: "
          f"{5/BPS*1000:.0f}ms — ambient")
    print(f"  Bass    R=7: "
          f"{7/BPS*1000:.0f}ms — navigational")
    print()
    print("  Structural symmetry:")
    print("  S1(FRICTION) ↔ S5(REFORMATION)")
    print("  S2(TENSION)  ↔ S4(FRACTURE)")
    print("  S3(TWIST) — axis of symmetry")
    print()
    print("  S3: voices become strings.")
    print("      strings become voices.")
    print("      The gap crossed by exchange.")
    print()

    print("Building score...")
    v1,v2,v3,v4 = build_fracture()
    voices = [v1,v2,v3,v4]
    print(f"  {sum(len(v) for v in voices)} "
          f"total notes")
    print()
    print("Rendering...")
    print()

    output = np.zeros(int(total_s*SR))

    all_agents = []
    for vi,part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part,i,SR,
                        seed=vi*100+i)
            for i in range(3)])

    for vi,(voice,agents) in enumerate(
            zip(voices,all_agents)):

        part  = PART_NAMES[vi]
        dr    = SPATIAL_DEPTH_FRACTURE[part]
        rev   = RoomReverb(rt60=2.0,sr=SR,
                           direct_ratio=dr)
        omult = OCTAVE_MULTIPLIERS[vi]
        cur   = 0
        beat  = 0.0

        for i,(pos,beats,vel) in \
                enumerate(voice):
            dur_s = beats/BPS
            n_s   = int(dur_s*SR)
            sec   = classify_fracture(
                beat, TOTAL_BEATS)
            sv    = string_axis_for(
                vi, sec, beat, TOTAL_BEATS)

            if pos is None:
                cur  += n_s
                beat += beats
                continue

            a,b   = pos
            coh   = coherence(a,b)
            freq  = ji_freq(a,b)*omult
            amp   = (vel/127.0)*0.50
            ppp   = vel/92.0

            vc,vn = vowel_fracture(
                vi,pos,sv,sec)
            gms   = glide_fracture(sv,dur_s)
            rev.set_rt60(
                rt60_fracture(sec,sv,coh))

            amp_envs,f1_envs = \
                compute_envelopes(
                    agents,dur_s,SR,
                    phrase_peak_prox=ppp)

            cents   = [0.0,+11.0,-17.0]
            vel_mod = int(vel*(0.7+0.3*coh))
            vel_mod = max(30,min(127,vel_mod))
            note_mix = np.zeros(n_s)

            for k in range(3):
                sig = render_note_textured(
                    freq, amp/3, dur_s,
                    vc, vn, gms, sv,
                    sr=SR,
                    velocity=vel_mod,
                    cents_offset=cents[k],
                    amp_env=amp_envs[k],
                    f1_agent_env=f1_envs[k])
                nm = min(len(sig),n_s)
                note_mix[:nm] += sig[:nm]

            processed = rev.process(note_mix)

            # Lean: string voices lean forward
            # (attack leading)
            # Voice voices lean back
            # (sustain trailing)
            if sv < 0.4:
                lean = -int(0.04*n_s)  # forward
            elif sv > 0.7:
                lean =  int(0.05*n_s*(1-coh))
            else:
                lean =  int(0.02*n_s*(1-coh))

            onset = max(0, cur+lean)
            end   = min(onset+len(processed),
                        len(output))
            seg   = end-onset
            if seg > 0:
                output[onset:end] += \
                    processed[:seg]

            cur  += n_s
            beat += beats

    mx = np.max(np.abs(output))
    if mx > 0:
        output = output/mx*0.82

    out_i   = (output*32767).astype(np.int16)
    outfile = "output_fracture/fracture.wav"
    with wave_module.open(outfile,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output)/SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.1f}s  "
          f"at {BPM}bpm")
    print()
    print("="*60)
    print()
    print("  afplay output_fracture/fracture.wav")
    print()
    print("  Section 3: the twist.")
    print("  The voices become strings.")
    print("  The strings become voices.")
    print("  You will feel the gap cross.")
    print("  Not by resolution.")
    print("  By exchange.")
    print()
    print("  Section 4: the fracture.")
    print("  The structure most visible")
    print("  at maximum stress.")
    print("  The skeleton showing.")
    print("  It does not fall.")
    print("  The guide knows the structural lines.")
    print("  You are inside them.")
    print()
    print("  Section 5: not home.")
    print("  A new shape.")
    print("  Containing the memory")
    print("  of the fracture.")
    print()
    print("  That is more interesting than home.")
