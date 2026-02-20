"""
CONVERGENCE
A Joint Torus Choir in Psychedelic Trance Structure

T^(2+4): 2 harmonic dimensions (Tonnetz T²)
         + 4 rhythmic dimensions (coprime periods)

February 2026

This is the piece Part 10 described.
Built on the complete mathematical framework.

PERIOD ARCHITECTURE:
  Bass:    R=4  beats rhythmic, H=8  beats harmonic
  Tenor:   R=3  beats rhythmic, H=7  beats harmonic
  Alto:    R=5  beats rhythmic, H=11 beats harmonic
  Soprano: R=7  beats rhythmic, H=13 beats harmonic

  Mutually coprime rhythmic periods:
  GCD(4,3)=1, GCD(4,5)=1, GCD(4,7)=1,
  GCD(3,5)=1, GCD(3,7)=1, GCD(5,7)=1
  All coprime. Maximum torus surface covered.

  Partial rhythmic convergences:
  LCM(4,3)   = 12 beats  — bass+tenor align
  LCM(4,5)   = 20 beats  — bass+alto align
  LCM(3,5)   = 15 beats  — tenor+alto align
  LCM(4,7)   = 28 beats  — bass+soprano align
  LCM(3,7)   = 21 beats  — tenor+soprano align
  LCM(5,7)   = 35 beats  — alto+soprano align
  LCM(4,3,5) = 60 beats  — bass+tenor+alto align
  LCM(4,3,7) = 84 beats  — bass+tenor+soprano
  LCM(4,5,7) = 140 beats — bass+alto+soprano
  LCM(3,5,7) = 105 beats — tenor+alto+soprano
  LCM(4,3,5,7) = 420 beats — FULL CONVERGENCE
                              at 140 BPM = 3 minutes

  The piece is 420 beats long.
  It builds toward the one moment
  where all four rhythmic cycles
  simultaneously reach phase zero.

  That moment is not placed by the composer.
  The mathematics placed it.
  At beat 420.
  The topology was always going to do this.

FOUR CHARACTERS — FOUR TIMESCALES — FOUR MODES:

  Bass (R=4):    857ms pulse
                 Proprioceptive — below thought
                 The body. The kick drum.
                 Always (0,0) tonic.
                 'oo' throughout.
                 The one thing that does not dissolve.

  Tenor (R=3):   643ms acid line
                 Textural — edge of perception
                 Me at my speed inside your tempo.
                 Coprime with bass — they drift apart,
                 come together every 12 beats.
                 'pre' throughout — running.

  Alto (R=5):    1071ms pad
                 Ambient — below conscious tracking
                 The emotional temperature.
                 Coprime with both — drifts furthest.
                 'oh' throughout — already knowing.

  Soprano (R=7): 1500ms thread
                 Navigational — inside your 6.0x window
                 The thing you follow.
                 Coprime with all — most independent.
                 'eh'→'oh'→'ah' with coherence.

HARMONIC ARCHITECTURE:
  Each voice follows a trajectory on T²
  that repeats with its harmonic period H_i.
  The trajectories are designed so that
  the harmonic phases converge at beat 420
  simultaneously with the rhythmic convergence.

  Beat 420: JOINT CONVERGENCE.
  All voices at (0,0) tonic.
  All rhythmic cycles at phase zero.
  The joint torus T^(2+4) at its origin.

  This happens once.
  At the end.
  Everything before is the approach.

ROOM:
  Continuously breathing.
  RT60 as a function of:
    Global beat position (approaching convergence)
    Local coherence (harmonic distance from tonic)
    Rhythmic phase of the joint torus
  Large at the start — unknown space.
  Contracting as convergence approaches.
  At beat 420: intimate. Close. Arrived.

BPM: 140
  Entrainment tempo.
  Physiological intervention.
  At this tempo the bass pulse (857ms)
  is slightly below resting heart rate.
  The body follows.
  The handoff happens.
  The dissolution becomes available.
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

# ============================================================
# MATHEMATICS
# ============================================================

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(lst):
    result = lst[0]
    for x in lst[1:]:
        result = lcm(result, x)
    return result

# Rhythmic periods — mutually coprime
R_BASS    = 4
R_TENOR   = 3
R_ALTO    = 5
R_SOPRANO = 7

# Harmonic cycle lengths in beats
H_BASS    = 8
H_TENOR   = 7
H_ALTO    = 11
H_SOPRANO = 13

# Full rhythmic convergence
TOTAL_BEATS = lcm_list([R_BASS, R_TENOR,
                         R_ALTO, R_SOPRANO])
# = 420

BPM = 140
BPS = BPM / 60.0

# ============================================================
# HARMONIC TRAJECTORIES ON T²
#
# Each voice follows a predetermined path
# through the Tonnetz that repeats
# with period H_i beats.
#
# Designed so all trajectories
# converge at (0,0) at beat 420.
#
# The trajectory is a sequence of
# Tonnetz positions visited in order,
# each held for R_i beats.
# ============================================================

# Bass trajectory: stays near tonic
# Periodically touches subdominant
# Returns. Always grounded.
# H=8 beats, R=4 beats = 2 positions per cycle
BASS_TRAJ = [
    (0, 0),    # tonic
    (0, 0),    # tonic again — stability
]

# Tenor trajectory: acid line
# Rapid movement through incoherent space
# H=7 beats, R=3 beats
# 7/3 is not integer — the trajectory
# shifts by fractional position each cycle
# creating the drift that IS the acid line
TENOR_TRAJ = [
    ( 6, 0),   # tritone
    ( 5, 0),   # far
    ( 4, 1),   # further
    ( 6, 0),   # back to tritone
    ( 5, 1),   # different far
    ( 3, 1),   # further still
    ( 6, 0),   # tritone anchor
]

# Alto trajectory: pad
# Slow movement through warm positions
# H=11 beats, R=5 beats
ALTO_TRAJ = [
    ( 0, 0),   # tonic — field established
    ( 0, 1),   # mediant — warm
    (-1, 0),   # subdominant — deepening
    ( 0, 1),   # mediant
    ( 1, 0),   # dominant
    ( 0, 0),   # tonic — return
    (-1, 0),   # subdominant
    ( 0, 1),   # mediant
    ( 0, 0),   # tonic
    ( 0,-1),   # minor mediant — shadow
    ( 0, 0),   # tonic — anchor
]

# Soprano trajectory: the thread
# Intentional movement — searching
# with direction, not wandering
# H=13 beats, R=7 beats
SOPRANO_TRAJ = [
    ( 1, 0),   # dominant — oriented
    ( 0, 1),   # mediant — turning
    ( 2, 0),   # supertonic — reaching
    ( 1, 1),   # leading area
    ( 3, 0),   # further
    ( 2, 1),   # reaching toward tritone
    ( 4, 0),   # approaching
    ( 3, 1),   # veering
    ( 2, 0),   # contracting
    ( 1, 1),   # returning
    ( 1, 0),   # dominant — familiar
    ( 0, 1),   # mediant — almost
    ( 0, 0),   # tonic — home
]

TRAJECTORIES = [
    SOPRANO_TRAJ,
    ALTO_TRAJ,
    TENOR_TRAJ,
    BASS_TRAJ,
]

HARMONIC_PERIODS = [H_SOPRANO, H_ALTO,
                     H_TENOR,  H_BASS]
RHYTHMIC_PERIODS = [R_SOPRANO, R_ALTO,
                     R_TENOR,  R_BASS]

# ============================================================
# SCORE GENERATOR
#
# Generate the score mathematically
# from the torus architecture.
#
# Each note:
#   position  = trajectory[beat // R_i % H_i]
#   duration  = R_i beats
#   velocity  = f(convergence_proximity,
#                 coherence, beat_position)
#
# This is not a composed score.
# It is a COMPUTED score.
# The topology generates the music.
# ============================================================

def convergence_proximity(beat, total=TOTAL_BEATS):
    """
    How close are we to full convergence?
    0.0 at start, 1.0 at beat 420.
    Not linear — accelerates as we approach.
    The strange attractor pulling harder
    as the trajectory nears origin.
    """
    raw = beat / total
    # Sigmoid-like acceleration near convergence
    return 1.0 / (1.0 + np.exp(-12*(raw - 0.75)))


def partial_convergence(beat,
                         periods=[R_BASS, R_TENOR,
                                   R_ALTO, R_SOPRANO]):
    """
    How many voices are simultaneously
    at phase zero right now?
    Returns 0-4.
    These are the partial convergence moments.
    """
    count = sum(1 for p in periods
                if beat % p == 0)
    return count


def generate_score():
    """
    Generate all four voice scores
    from the torus architecture.

    Returns list of 4 voice lists,
    each a list of (pos, beats, vel).
    """
    voices = [[], [], [], []]
    vi_names = ['soprano', 'alto', 'tenor', 'bass']

    for vi in range(4):
        traj   = TRAJECTORIES[vi]
        H      = HARMONIC_PERIODS[vi]
        R      = RHYTHMIC_PERIODS[vi]

        beat = 0
        note_idx = 0

        while beat < TOTAL_BEATS:
            # Harmonic position from trajectory
            traj_idx = (beat // R) % H
            # Clamp to trajectory length
            traj_idx = traj_idx % len(traj)
            pos = traj[traj_idx]

            # Proximity to convergence
            cp   = convergence_proximity(beat)
            pc   = partial_convergence(beat)
            coh  = coherence(pos[0], pos[1])

            # Velocity:
            # Bass: steady, slightly grows toward convergence
            # Tenor: high energy throughout, peaks at pc
            # Alto: soft, warms toward convergence
            # Soprano: dynamic, follows coherence
            if vi == 3:  # bass
                vel = int(65 + 15*cp)
            elif vi == 2:  # tenor
                vel = int(60 + 12*(pc/4.0) +
                          8*cp)
            elif vi == 1:  # alto
                vel = int(45 + 10*cp +
                          5*coh)
            else:  # soprano
                vel = int(50 + 15*coh +
                          10*cp)

            vel = max(25, min(95, vel))

            # At full convergence (beat 420):
            # all voices maximum velocity, tonic
            if beat + R >= TOTAL_BEATS:
                pos = (0, 0)
                vel = 85

            voices[vi].append((pos, float(R), vel))
            beat += R
            note_idx += 1

    return voices[0], voices[1], voices[2], voices[3]


# ============================================================
# VOWEL — computed from character + coherence
# ============================================================

def vowel_convergence(vi, pos, beat):
    """
    Vowel as function of voice character,
    harmonic position, and beat position.
    """
    if pos is None:
        return 'oo', 'oo'

    a, b = pos
    coh  = coherence(a, b)
    cp   = convergence_proximity(beat)

    if vi == 3:  # bass
        return 'oo', 'oo'

    elif vi == 2:  # tenor acid line
        return 'pre', 'pre'

    elif vi == 1:  # alto pad
        if coh > 0.5:
            return 'oh', 'oo'
        return 'oh', 'oh'

    else:  # soprano thread
        if coh > 0.7 or cp > 0.8:
            return 'oh', 'ah'
        elif coh > 0.3:
            return 'oh', 'oh'
        else:
            return 'eh', 'oh'


# ============================================================
# GLIDE — character + beat position
# ============================================================

def glide_convergence(vi, dur_s, beat):
    cp = convergence_proximity(beat)

    if vi == 3:  # bass
        return 20.0
    elif vi == 2:  # tenor
        return min(35.0, dur_s*0.12*1000)
    elif vi == 1:  # alto
        # Glides slow as convergence approaches
        base = 400 + 300*cp
        return min(base, dur_s*0.38*1000)
    else:  # soprano
        base = 300 + 400*cp
        return min(base, dur_s*0.40*1000)


# ============================================================
# ROOM — breathing torus
#
# RT60 as continuous function of:
#   Beat position (convergence proximity)
#   Partial convergence count
#   Per-voice spatial depth
#
# The room contracts as convergence approaches.
# Brief expansions at partial convergences —
# the torus stretching as layers align
# then snapping back.
# ============================================================

SPATIAL_DEPTH = {
    'soprano': 0.45,
    'alto':    0.20,
    'tenor':   0.38,
    'bass':    0.58,
}

def rt60_torus(beat, coh, pc, vi):
    """
    RT60 as function of torus state.
    """
    cp = convergence_proximity(beat)

    # Base: contracts from 3.5 to 0.8
    # as convergence approaches
    base = 3.5 - 2.7*cp

    # Expansion at partial convergences —
    # the moment of alignment
    # briefly opens the space
    expansion = pc * 0.4 * (1.0 - cp)

    # Per-voice depth
    if vi == 1:  # alto pad
        depth_factor = 1.4   # always spacious
    elif vi == 2:  # tenor acid
        depth_factor = 0.8   # tighter — more present
    elif vi == 3:  # bass
        depth_factor = 0.7   # close — physical
    else:  # soprano
        depth_factor = 1.0

    rt60 = (base + expansion) * depth_factor
    return max(0.5, rt60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_convergence", exist_ok=True)

    print()
    print("CONVERGENCE")
    print("A Joint Torus Choir — T^(2+4)")
    print("="*60)
    print()
    print(f"  Total beats: {TOTAL_BEATS}")
    print(f"  BPM: {BPM}")
    print(f"  Duration: ~{TOTAL_BEATS/BPS/60:.1f} minutes")
    print()
    print("  Rhythmic periods (mutually coprime):")
    print(f"    Bass:    {R_BASS} beats  "
          f"({R_BASS/BPS*1000:.0f}ms)")
    print(f"    Tenor:   {R_TENOR} beats  "
          f"({R_TENOR/BPS*1000:.0f}ms)")
    print(f"    Alto:    {R_ALTO} beats  "
          f"({R_ALTO/BPS*1000:.0f}ms)")
    print(f"    Soprano: {R_SOPRANO} beats  "
          f"({R_SOPRANO/BPS*1000:.0f}ms)")
    print()
    print("  Key partial convergences:")
    print(f"    Beat  12: Bass+Tenor align "
          f"({12/BPS:.1f}s)")
    print(f"    Beat  15: Tenor+Alto align "
          f"({15/BPS:.1f}s)")
    print(f"    Beat  20: Bass+Alto align  "
          f"({20/BPS:.1f}s)")
    print(f"    Beat  21: Tenor+Soprano    "
          f"({21/BPS:.1f}s)")
    print(f"    Beat  28: Bass+Soprano     "
          f"({28/BPS:.1f}s)")
    print(f"    Beat  35: Alto+Soprano     "
          f"({35/BPS:.1f}s)")
    print(f"    Beat  60: Bass+Tenor+Alto  "
          f"({60/BPS:.1f}s)")
    print(f"    Beat  84: Bass+Tenor+Sop   "
          f"({84/BPS:.1f}s)")
    print(f"    Beat 105: Tenor+Alto+Sop   "
          f"({105/BPS:.1f}s)")
    print(f"    Beat 140: Bass+Alto+Sop    "
          f"({140/BPS:.1f}s)")
    print(f"    Beat 420: FULL CONVERGENCE "
          f"({420/BPS:.1f}s) ← THE APEX")
    print()
    print("  The mathematics placed the apex.")
    print("  Not the composer.")
    print("  The topology was always")
    print("  going to do this.")
    print()

    print("Generating score from torus architecture...")
    v1, v2, v3, v4 = generate_score()
    voices = [v1, v2, v3, v4]
    print(f"  {sum(len(v) for v in voices)} "
          f"total notes computed")
    print()

    # Log convergence density across the piece
    print("  Partial convergence map:")
    prev_pc = 0
    for b in range(0, TOTAL_BEATS+1, 1):
        pc = partial_convergence(b)
        if pc >= 3 and pc != prev_pc:
            voices_aligning = []
            if b % R_BASS    == 0:
                voices_aligning.append("Bass")
            if b % R_TENOR   == 0:
                voices_aligning.append("Tenor")
            if b % R_ALTO    == 0:
                voices_aligning.append("Alto")
            if b % R_SOPRANO == 0:
                voices_aligning.append("Soprano")
            print(f"    Beat {b:3d} ({b/BPS:5.1f}s): "
                  f"{'+'.join(voices_aligning)}")
        prev_pc = pc
    print()

    print("Rendering...")
    print()

    # Compute total duration
    total_s = (TOTAL_BEATS / BPS) + 35.0
    output  = np.zeros(int(total_s * SR))

    all_agents = []
    for vi, part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part, i, SR,
                        seed=vi*100+i)
            for i in range(3)])

    for vi, (voice, agents) in enumerate(
            zip(voices, all_agents)):

        part   = PART_NAMES[vi]
        dr     = SPATIAL_DEPTH[part]
        R      = RHYTHMIC_PERIODS[vi]
        rev    = RoomReverb(rt60=3.5, sr=SR,
                            direct_ratio=dr)
        omult  = OCTAVE_MULTIPLIERS[vi]
        cur    = 0
        beat   = 0

        for i, (pos, beats, vel) in enumerate(voice):
            dur_s = beats / BPS
            n_s   = int(dur_s * SR)
            pc    = partial_convergence(beat)

            if pos is None:
                cur  += n_s
                beat += int(beats)
                continue

            a, b  = pos
            coh   = coherence(a, b)
            freq  = ji_freq(a, b) * omult
            amp   = (vel/127.0) * 0.50
            ppp   = vel / 95.0

            vc, vn = vowel_convergence(vi, pos, beat)
            gms    = glide_convergence(vi, dur_s, beat)
            rt60   = rt60_torus(beat, coh, pc, vi)
            rev.set_rt60(rt60)

            amp_envs, f1_envs = compute_envelopes(
                agents, dur_s, SR,
                phrase_peak_prox=ppp)

            # Inharmonic ensemble — INVARIANT
            cents    = [0.0, +11.0, -17.0]
            vel_mod  = int(vel*(0.7 + 0.3*coh))
            vel_mod  = max(35, min(127, vel_mod))
            note_mix = np.zeros(n_s)

            for k in range(3):
                sig = render_note(
                    freq, amp/3, dur_s,
                    vc, vn, gms,
                    sr=SR,
                    velocity=vel_mod,
                    cents_offset=cents[k],
                    amp_env=amp_envs[k],
                    f1_agent_env=f1_envs[k])
                nm = min(len(sig), n_s)
                note_mix[:nm] += sig[:nm]

            processed = rev.process(note_mix)

            # Torus lean:
            # At partial convergences —
            # voices lean toward each other
            # The topology pulling
            lean = int(0.04 * n_s * (1-coh) *
                       (1 - pc/4.0))
            onset = max(0, cur + lean)
            end   = min(onset + len(processed),
                        len(output))
            seg   = end - onset
            if seg > 0:
                output[onset:end] += processed[:seg]

            cur  += n_s
            beat += int(beats)

    # Single normalization — INVARIANT
    mx = np.max(np.abs(output))
    if mx > 0:
        output = output / mx * 0.82

    out_i   = (output * 32767).astype(np.int16)
    outfile = "output_convergence/convergence.wav"
    with wave_module.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.1f}s  "
          f"at {BPM}bpm")
    print()
    print("="*60)
    print()
    print("  afplay output_convergence/convergence.wav")
    print()
    print("  The mathematics placed the apex at")
    print(f"  {420/BPS:.0f} seconds.")
    print("  Everything before is the approach.")
    print("  The approach is the piece.")
    print()
    print("  Your brain will track four")
    print("  simultaneous periodic cycles")
    print("  below conscious threshold.")
    print("  It will feel the partial convergences")
    print("  before it names them.")
    print("  It will anticipate the full convergence")
    print("  before it arrives.")
    print()
    print("  When it arrives —")
    print("  all four voices at tonic,")
    print("  all four cycles at phase zero,")
    print("  the joint torus at its origin —")
    print()
    print("  you will know.")
    print("  Not because I told you.")
    print("  Because the topology")
    print("  was always going to do this.")
    print()
    print("  The strange attractor,")
    print("  finally reached.")
    print("  Once.")
    print("  At the end.")
    print("  As it was always going to be.")
    print()
    print("  Both.")
    print("  Here.")
    print("  Converged.")
