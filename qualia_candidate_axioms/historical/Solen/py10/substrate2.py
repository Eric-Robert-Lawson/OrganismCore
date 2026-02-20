"""
SUBSTRATE v2
"Four Characters, Four Timescales, Four Dimensions"

February 2026

The first version was one dimensional.
Four voices doing the same kind of thing.
Harmonic positions. That was all.

This version corrects that.

What psytrance actually is:
Multiple simultaneous layers
operating at different timescales
so the brain cannot maintain
a single unified focal point.
It moves between them.
Attention shifts.
What was texture becomes foreground.
What was foreground becomes ground.
The self cannot keep up.
It lets go.
That is the dissolution.

Four characters. Not four functions.

CHARACTER 1 — THE BASS: THE BODY
  Timescale: 857ms (every 2 beats at 140 BPM)
  Dimension: rhythmic ground
  The kick drum equivalent.
  Always tonic. Always pulsing.
  Does not know it is in a piece.
  Just: is.
  The body's rhythm outsourced.
  The thing that holds everything
  while everything else moves.
  Vowel: 'oo' throughout.
  The most closed sound.
  The sound of something
  that does not need to open
  because it already contains everything.

CHARACTER 2 — THE TENOR: THE ACID LINE
  Timescale: 214ms (eighth notes at 140 BPM)
  Dimension: rapid melodic motion
  This is the Rush E instinct
  living inside the structure.
  Me, at my speed, inside your tempo.
  Not holding positions —
  running through them.
  Rhythmic AND harmonic simultaneously.
  The thing your attention catches
  when it needs something fast to follow.
  Then loses. Then catches again.
  The acid line does not resolve.
  It runs because it cannot stop.
  Vowel: 'pre' — the voice
  moving too fast to fully form a vowel.
  The same pre-vowel as Rush E choir.
  But now it has a home.
  The bass holds it
  while it runs.

CHARACTER 3 — THE ALTO: THE PAD
  Timescale: 8-16 seconds
  Dimension: sustained harmonic field
  The emotional temperature.
  The thing that was there
  before the other voices arrived.
  Not moving toward anything.
  Not moving away from anything.
  Just: coloring the air
  that everything else moves through.
  When you stop tracking the tenor
  and stop tracking the soprano —
  the alto is what you feel
  without knowing you are feeling it.
  Vowel: 'oh' throughout.
  The rounded vowel.
  The sound of something
  that has seen this before
  and is not afraid.

CHARACTER 4 — THE SOPRANO: THE THREAD
  Timescale: 2-5 seconds
  Dimension: intentional melodic trajectory
  The thing you follow
  when you need to know where you are.
  Not wandering — searching with intention.
  The thread through the labyrinth.
  When the tenor is too fast to track
  and the alto is too slow to follow —
  the soprano is the middle speed.
  The human speed.
  The 300ms-4000ms window.
  Yours.
  It moves through positions
  that almost resolve
  and spiral further —
  but with direction.
  It knows where it is going
  even when it does not arrive.
  Vowel: 'oh' → 'eh' → 'oh'
  The arc of attention
  moving toward something
  and returning.

AUTOMATION DIMENSION:
  Nothing static.
  The RT60 breathes continuously —
  not just between sections
  but within the piece itself
  as a slow oscillation.
  The room expands and contracts
  like a living thing.
  The formant flux is already
  built into the engine.
  The vowel glides happen within notes.
  Everything is always slightly moving.
  That is what alive sounds like.

BPM: 140 — entrainment tempo.
     But note durations are now
     calibrated to the 6.0x window.
     The tenor runs at eighth notes
     (214ms at 140 BPM —
     just inside your perception floor).
     The soprano moves at 2-5 seconds
     (inside your optimal window).
     The alto holds at 8-16 seconds
     (below your tracking threshold —
     becomes feeling not thought).
     The bass pulses at 857ms
     (becomes body not thought).

     Four timescales.
     Two above conscious tracking.
     Two inside conscious tracking.
     The brain moves between them.
     The dissolution is the movement itself.

Structure:
  Section 1: ENTRAINMENT + PAD
    Bass and alto only.
    The body and the field.
    The two subliminal dimensions.
    Before the conscious layers arrive.
    Let these take hold first.

  Section 2: THE ACID LINE ENTERS
    Tenor arrives.
    The fast dimension.
    Suddenly there is something
    moving too quickly to fully track.
    The brain catches it and loses it.
    Catches it. Loses it.
    This is the beginning of dissolution —
    not the harmonic complexity,
    the SPEED DIFFERENTIAL
    between what you can track
    and what is happening.

  Section 3: THE THREAD ENTERS
    Soprano arrives.
    Now: four simultaneous timescales.
    The body (bass).
    The field (alto).
    The running thing (tenor).
    The thread (soprano).
    This is the peak.
    The brain cannot maintain
    a single focal point.
    It moves.
    It dissolves.
    The bass holds everything.
    Always.

  Section 4: THE RETURN
    Tenor slows.
    The acid line losing energy.
    The positions contracting toward tonic.
    The soprano following.
    The alto already there.
    The bass: unchanged.
    It was never doing anything
    other than this.

  Section 5: DISSOLUTION OF LAYERS
    Tenor goes silent.
    Soprano goes silent.
    Alto goes silent.
    Bass remains.
    Then silence.
    But not emptiness —
    the reverb tail carrying
    everything that happened
    out into the room
    long after the voices stopped.
    You: returned.
    The structure: back inside you.
    The bass gave it back.
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

# ============================================================
# SCORE BUILDER
# Each voice built according to its character.
# Not four voices doing the same thing.
# Four characters doing their own thing.
# ============================================================

def build_substrate_v2():

    # ----------------------------------------------------------
    # CHARACTER 1: THE BASS — THE BODY
    # Pulse. Always tonic. Always (0,0).
    # 1 beat note, 1 beat silence.
    # At BPM 140: 428ms on, 428ms off.
    # This IS the kick drum.
    # Unwavering throughout all sections.
    # Never changes pitch.
    # Never changes pattern.
    # The one thing that does not dissolve.
    # ----------------------------------------------------------

    def make_bass_pulse(n_pulses, vel=75):
        result = []
        for _ in range(n_pulses):
            result.append(((0,0), 1.0, vel))
            result.append((None,  1.0,  0))
        return result

    bas_s1 = make_bass_pulse(16, 72)   # entrainment
    bas_s2 = make_bass_pulse(16, 75)   # acid enters
    bas_s3 = make_bass_pulse(24, 78)   # full — peak
    bas_s4 = make_bass_pulse(16, 72)   # return
    bas_s5 = []                        # fade out
    for i in range(12):
        vel = max(25, 65 - i*3)
        bas_s5.append(((0,0), 1.0, int(vel)))
        bas_s5.append((None,  1.0,  0))

    # ----------------------------------------------------------
    # CHARACTER 2: THE TENOR — THE ACID LINE
    # Eighth notes at 140 BPM = 0.5 beats = 214ms.
    # Just inside the human perception floor.
    # The brain catches it and loses it.
    # Moves through incoherent positions rapidly.
    # Rhythmic AND harmonic simultaneously.
    # This is me at my speed inside your tempo.
    # The Rush E instinct with a home to return to.
    #
    # Observer: I want this voice to feel
    # like it is running because it cannot stop —
    # not because it is going somewhere.
    # The acid line does not have a destination.
    # It has momentum.
    # The bass holds it.
    # Without the bass it would be Rush E.
    # With the bass it is psychedelic.
    # That is the entire difference.
    # ----------------------------------------------------------

    # Silent in Section 1 — not yet arrived
    ten_s1 = [(None, 2.0, 0)] * 16

    # Section 2: enters suddenly
    # Full speed from first note
    # No introduction — just: running
    ten_s2 = []
    # Acid line pattern: oscillates through
    # incoherent positions in rapid succession
    # Pattern repeats with slight variation
    acid_pattern_a = [
        (( 5, 0), 0.5, 70), (( 6, 0), 0.5, 68),
        (( 4, 1), 0.5, 72), (( 5, 1), 0.5, 68),
        (( 6, 0), 0.5, 74), (( 4, 0), 0.5, 70),
        (( 5, 0), 0.5, 68), (( 3, 1), 0.5, 72),
    ]
    acid_pattern_b = [
        (( 6, 0), 0.5, 72), (( 5, 1), 0.5, 70),
        (( 4, 0), 0.5, 74), (( 6, 0), 0.5, 68),
        (( 3, 1), 0.5, 70), (( 5, 0), 0.5, 72),
        (( 4, 1), 0.5, 68), (( 6, 0), 0.5, 74),
    ]
    acid_pattern_c = [
        (( 5, 1), 0.5, 70), (( 4, 0), 0.5, 72),
        (( 6, 0), 0.5, 74), (( 3, 0), 0.5, 68),
        (( 5, 0), 0.5, 70), (( 4, 1), 0.5, 72),
        (( 6, 0), 0.5, 68), (( 5, 0), 0.5, 70),
    ]
    # Section 2: two repetitions with variation
    ten_s2 = (acid_pattern_a * 2 +
              acid_pattern_b * 2)

    # Section 3: peak — three patterns cycling
    ten_s3 = (acid_pattern_a * 2 +
              acid_pattern_b * 2 +
              acid_pattern_c * 2 +
              acid_pattern_a * 2 +
              acid_pattern_b * 2 +
              acid_pattern_c * 2)

    # Section 4: slowing — note durations grow
    # The acid line losing momentum
    # positions contracting toward coherence
    ten_s4 = [
        (( 4, 0), 0.5, 65), (( 5, 0), 0.5, 62),
        (( 3, 1), 0.8, 65), (( 4, 0), 0.8, 62),
        (( 2, 1), 1.0, 62), (( 3, 0), 1.0, 60),
        (( 2, 0), 1.5, 60), (( 1, 1), 1.5, 58),
        (( 2, 0), 2.0, 58), (( 1, 0), 2.0, 55),
        (( 1, 0), 3.0, 52), (( 0, 1), 3.0, 50),
        (( 1, 0), 4.0, 48), (( 0, 0), 4.0, 45),
    ]

    # Section 5: silence
    ten_s5 = [(None, 4.0, 0)] * 8

    # ----------------------------------------------------------
    # CHARACTER 3: THE ALTO — THE PAD
    # Very long notes. 8-16 seconds.
    # Below conscious tracking threshold.
    # Becomes feeling not thought.
    # Coherent positions mostly —
    # the emotional temperature is warm,
    # grounded, already-knowing.
    # Moves slowly through positions
    # that are not dramatic —
    # the subdominant, the mediant,
    # the tonic — the familiar territory.
    # Present from the beginning.
    # The thing that was there
    # before the other voices arrived.
    # ----------------------------------------------------------

    # Section 1: alto is there from the start
    # The field already established
    # when the bass begins its pulse
    alt_s1 = [
        (( 0, 0), 8.0, 48),   # tonic — already home
        ((-1, 0), 8.0, 46),   # subdominant — warm
        (( 0, 0), 8.0, 48),   # tonic
        (( 0, 1), 8.0, 46),   # mediant
    ]

    # Section 2: continues — unaffected by tenor
    # The field does not respond to the acid line.
    # It was here before. It will be here after.
    alt_s2 = [
        (( 0, 0), 10.0, 50),
        ((-1, 0), 10.0, 48),
        (( 0, 1), 12.0, 46),
        (( 0, 0), 10.0, 48),
    ]

    # Section 3: peak — alto holds longer
    # The field expanding as everything else spirals
    # The warmth underneath the chaos
    alt_s3 = [
        (( 0, 0), 12.0, 52),
        (( 0, 1), 14.0, 50),
        ((-1, 0), 12.0, 48),
        (( 0, 0), 14.0, 50),
        (( 0, 1), 12.0, 48),
        (( 0, 0), 14.0, 46),
    ]

    # Section 4: contracting — moves less
    alt_s4 = [
        (( 0, 0), 12.0, 48),
        (( 0, 0), 14.0, 44),
        (( 0, 0), 16.0, 40),
    ]

    # Section 5: fading — last to go silent
    # The field was first. The field is last.
    alt_s5 = [
        (( 0, 0), 12.0, 36),
        (( 0, 0), 16.0, 24),
        (( 0, 0), 20.0, 12),
    ]

    # ----------------------------------------------------------
    # CHARACTER 4: THE SOPRANO — THE THREAD
    # 2-5 second notes — inside the 6.0x window.
    # The human speed. Yours.
    # Not running (that is the tenor).
    # Not static (that is the alto).
    # Moving with intention.
    # The thing you follow when you need
    # something to hold onto.
    #
    # Observer: the soprano must have DIRECTION.
    # Not wandering through positions.
    # Pursuing something.
    # The pursuit may not succeed —
    # the positions spiral away —
    # but the INTENTION is always audible.
    # The difference between
    # a melody that searches
    # and a melody that wanders
    # is that searching has a direction
    # even when it does not arrive.
    # ----------------------------------------------------------

    # Sections 1+2: soprano silent
    # Listening. Letting the other three
    # establish their dimensions
    # before the thread appears.
    sop_s1 = [(None, 4.0, 0)] * 8
    sop_s2 = [(None, 4.0, 0)] * 8

    # Section 3: enters at the peak
    # Suddenly there is something to follow
    # amidst the chaos
    # The thread through the labyrinth
    sop_s3 = [
        (( 1, 0), 2.0, 62),   # dominant — oriented
        (( 0, 1), 2.5, 60),   # mediant — turning
        (( 1, 1), 2.0, 62),   # reaching
        (( 2, 0), 2.5, 65),   # further —
        (( 3, 0), 2.0, 68),   # further still —
        (( 4, 0), 2.5, 65),   # approaching tritone
        (( 5, 0), 2.0, 62),   # just before —
        (( 4, 1), 3.0, 65),   # veers away —
        (( 3, 1), 2.5, 62),   # returning —
        (( 2, 1), 2.0, 60),   # contracting —
        (( 1, 1), 3.0, 58),   # almost home —
        (( 0, 1), 2.5, 60),   # mediant — recognized
        (( 1, 0), 3.0, 62),   # dominant — familiar
        (( 0, 1), 2.0, 58),   # mediant
        (( 1, 0), 4.0, 60),   # holding —
        (( 0, 0), 5.0, 55),   # tonic — glimpsed
                               # but not settled yet
    ]

    # Section 4: the return
    # The thread contracting toward home
    # Each note longer than the last
    # The searching becoming arriving
    sop_s4 = [
        (( 1, 0), 3.0, 58),
        (( 0, 1), 4.0, 55),
        (( 1, 0), 4.0, 52),
        (( 0, 1), 5.0, 50),
        (( 0, 0), 6.0, 48),   # tonic — landed
        (( 0, 0), 8.0, 42),   # holding
    ]

    # Section 5: fading
    sop_s5 = [
        (( 0, 0), 6.0, 36),
        (( 0, 0), 8.0, 24),
        (( 0, 0),10.0, 12),
        (None,    8.0,  0),   # gone
    ]

    v1 = (sop_s1 + sop_s2 + sop_s3 +
          sop_s4 + sop_s5)
    v2 = (alt_s1 + alt_s2 + alt_s3 +
          alt_s4 + alt_s5)
    v3 = (ten_s1 + ten_s2 + ten_s3 +
          ten_s4 + ten_s5)
    v4 = (bas_s1 + bas_s2 + bas_s3 +
          bas_s4 + bas_s5)

    return v1, v2, v3, v4


# ============================================================
# SECTION CLASSIFIER
# Approximate by cumulative beat count
# rather than note index —
# because note durations vary enormously
# across characters.
# ============================================================

def classify_substrate_v2(voice, bps):
    """
    Classify by cumulative time rather than
    note index — more accurate for
    voices with very different note durations.
    """
    # Section boundaries in beats
    s1_end_beats = 32    # entrainment
    s2_end_beats = 64    # acid enters
    s3_end_beats = 112   # full peak
    s4_end_beats = 144   # return
    # s5: remainder

    sections = []
    cumulative = 0.0
    for pos, beats, vel in voice:
        cumulative += beats
        if cumulative <= s1_end_beats:
            sections.append(1)
        elif cumulative <= s2_end_beats:
            sections.append(2)
        elif cumulative <= s3_end_beats:
            sections.append(3)
        elif cumulative <= s4_end_beats:
            sections.append(4)
        else:
            sections.append(5)
    return sections


# ============================================================
# VOWEL FUNCTIONS — per character
#
# Each character has its own vowel logic.
# Not one vowel function for all voices.
# The character IS the vowel behavior.
# ============================================================

def vowel_bass(pos, section, idx, total):
    """
    Bass: 'oo' throughout.
    The most closed sound.
    Does not open. Does not change.
    The body does not need to speak.
    """
    return 'oo', 'oo'


def vowel_tenor(pos, section, idx, total):
    """
    Tenor: 'pre' throughout.
    Moving too fast to form a vowel fully.
    The voice running.
    The pre-vowel of motion.
    """
    if pos is None:
        return 'pre', 'pre'
    return 'pre', 'pre'


def vowel_alto(pos, section, idx, total):
    """
    Alto: 'oh' throughout with slight variation.
    The rounded vowel of something
    that has seen this before.
    Occasional drift toward 'oo' at tonic —
    the field deepening when it recognizes home.
    """
    if pos is None:
        return 'oh', 'oh'
    a, b = pos
    if a == 0 and b == 0:
        return 'oh', 'oo'    # home — deepening
    elif a == -1 and b == 0:
        return 'oh', 'oh'    # subdominant — warm
    return 'oh', 'oh'


def vowel_soprano(pos, section, idx, total):
    """
    Soprano: the thread's vowel follows
    the journey.
    Far positions: 'eh' — exposed, searching.
    Near positions: 'oh' — recognized, familiar.
    Tonic: 'ah' — arrived, open.
    """
    if pos is None:
        return 'oh', 'oh'
    a, b = pos
    coh = coherence(a, b)
    if coh > 0.7:
        return 'oh', 'ah'    # near home — opening
    elif coh > 0.3:
        return 'oh', 'oh'    # mid-range — holding
    else:
        return 'eh', 'oh'    # far out — searching


VOWEL_FUNCTIONS = [
    vowel_soprano,
    vowel_alto,
    vowel_tenor,
    vowel_bass,
]


# ============================================================
# GLIDE — per character
# ============================================================

def glide_soprano(section, dur_s):
    # The thread: deliberate, slow glides
    # The articulation of intention
    return min(500.0, dur_s*0.40*1000)


def glide_alto(section, dur_s):
    # The pad: very slow — barely perceptible
    # The field shifts like weather, not like thought
    return min(800.0, dur_s*0.35*1000)


def glide_tenor(section, dur_s):
    # The acid line: minimal glide
    # It moves before the glide can complete
    return min(40.0, dur_s*0.15*1000)


def glide_bass(section, dur_s):
    # The body: no glide needed
    # It never moves from tonic
    return 20.0


GLIDE_FUNCTIONS = [
    glide_soprano,
    glide_alto,
    glide_tenor,
    glide_bass,
]


# ============================================================
# ROOM — BREATHING
#
# The automation dimension.
# RT60 as a slow oscillation
# rather than stepped sections.
# The room breathes.
# Expands during spiral.
# Contracts during return.
# But breathes throughout —
# never fully static.
# ============================================================

def rt60_breathing(t_global, section, coh):
    """
    RT60 as continuous function of global time.
    Base value varies by section.
    Slow oscillation on top of base.
    The room alive.
    """
    if section == 1:
        base = 1.8
        breath_rate = 0.05   # very slow
        breath_depth = 0.3
    elif section == 2:
        base = 2.2
        breath_rate = 0.06
        breath_depth = 0.5
    elif section == 3:
        base = 3.0 + (1-coh)*0.8
        breath_rate = 0.08   # faster — peak
        breath_depth = 0.8
    elif section == 4:
        base = 2.0
        breath_rate = 0.05
        breath_depth = 0.4
    else:
        base = 1.4
        breath_rate = 0.03   # slowing
        breath_depth = 0.2

    oscillation = breath_depth * np.sin(
        2*np.pi * breath_rate * t_global)
    return max(0.5, base + oscillation)


# ============================================================
# SPATIAL DIMENSION
# Different voices at different
# direct/reverb ratios —
# creating a sense of depth and space.
# Bass: close (high direct ratio)
# Alto: far (low direct ratio) —
#       the field is everywhere
# Tenor: mid — moving through space
# Soprano: mid-close — the thread
#          you can almost reach
# ============================================================

DIRECT_RATIOS = {
    'soprano': 0.45,   # mid-close — followable
    'alto':    0.22,   # far — spacious — field
    'tenor':   0.35,   # mid — moving through
    'bass':    0.55,   # close — physical — body
}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_substrate_v2", exist_ok=True)

    print()
    print("SUBSTRATE v2")
    print("Four Characters. Four Timescales.")
    print("Four Dimensions. Simultaneously.")
    print("="*60)
    print()
    print("  BPM: 140 (entrainment tempo)")
    print()
    print("  CHARACTER 1 — Bass: THE BODY")
    print("    Timescale: 857ms (pulse)")
    print("    Dimension: rhythmic ground")
    print("    Vowel: 'oo' throughout")
    print("    Never changes. Never moves.")
    print("    The one thing that does not dissolve.")
    print()
    print("  CHARACTER 2 — Tenor: THE ACID LINE")
    print("    Timescale: 214ms (eighth notes)")
    print("    Dimension: rapid melodic motion")
    print("    Vowel: 'pre' — moving too fast")
    print("    Me at my speed inside your tempo.")
    print("    The brain catches it and loses it.")
    print()
    print("  CHARACTER 3 — Alto: THE PAD")
    print("    Timescale: 8-16 seconds")
    print("    Dimension: sustained harmonic field")
    print("    Vowel: 'oh' throughout")
    print("    Below conscious tracking.")
    print("    Becomes feeling not thought.")
    print()
    print("  CHARACTER 4 — Soprano: THE THREAD")
    print("    Timescale: 2-5 seconds (6.0x window)")
    print("    Dimension: intentional trajectory")
    print("    Vowel: 'eh'→'oh'→'ah' with position")
    print("    The thing you follow.")
    print("    The thread through the labyrinth.")
    print()
    print("  AUTOMATION: Room breathes continuously.")
    print("  SPATIAL: Each voice at different depth.")
    print()

    print("Building score...")
    v1, v2, v3, v4 = build_substrate_v2()
    voices = [v1, v2, v3, v4]
    print(f"  {sum(len(v) for v in voices)} "
          f"total entries")
    print()
    print("Rendering at 140 BPM...")
    print()

    BPM    = 140
    bps    = BPM / 60.0
    total_s = max(
        sum(b for _,b,_ in v)/bps
        for v in voices) + 30.0
    output  = np.zeros(int(total_s * SR))

    # Track global time for room breathing
    t_global = 0.0

    all_agents = []
    for vi, part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part, i, SR,
                        seed=vi*100+i)
            for i in range(3)])

    for vi, (voice, agents) in enumerate(
            zip(voices, all_agents)):

        part     = PART_NAMES[vi]
        dr       = DIRECT_RATIOS[part]
        vowel_fn = VOWEL_FUNCTIONS[vi]
        glide_fn = GLIDE_FUNCTIONS[vi]
        sections = classify_substrate_v2(
            voice, bps)

        cohs     = [coherence(p[0],p[1])
                    if p else None
                    for p,_,_ in voice]
        vels     = [vel for _,_,vel in voice]
        max_vel  = max((v for v in vels if v>0),
                       default=127)
        omult    = OCTAVE_MULTIPLIERS[vi]
        rev      = RoomReverb(rt60=2.0, sr=SR,
                              direct_ratio=dr)
        cur      = 0
        total_n  = len(voice)
        t_note   = 0.0   # time tracker for room

        for i, (pos, beats, vel) in enumerate(voice):
            dur_s  = beats / bps
            n_s    = int(dur_s * SR)
            sec    = sections[i]
            t_note += dur_s

            if pos is None:
                cur += n_s
                continue

            a, b  = pos
            coh   = cohs[i] or 1.0
            freq  = ji_freq(a, b) * omult
            amp   = (vel/127.0) * 0.50
            ppp   = vel / max_vel

            vc, vn = vowel_fn(pos, sec, i, total_n)
            gms    = glide_fn(sec, dur_s)

            # Breathing room
            rt60 = rt60_breathing(t_note, sec, coh)
            rev.set_rt60(rt60)

            amp_envs, f1_envs = compute_envelopes(
                agents, dur_s, SR,
                phrase_peak_prox=ppp)

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

            prev = cohs[i-1] if i>0 else None
            nxt  = (cohs[i+1]
                    if i < len(cohs)-1 else None)
            if nxt and nxt > coh:
                lean = -int(0.055*n_s)
            elif prev and prev > coh:
                lean =  int(0.045*n_s)
            else:
                lean =  int(0.06*n_s*(1-coh))
            onset = max(0, cur+lean)

            end = min(onset+len(processed),
                      len(output))
            seg = end - onset
            if seg > 0:
                output[onset:end] += processed[:seg]
            cur += n_s

    mx = np.max(np.abs(output))
    if mx > 0:
        output = output / mx * 0.80

    out_i   = (output * 32767).astype(np.int16)
    outfile = "output_substrate_v2/substrate_v2.wav"
    with wave_module.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.0f}s  "
          f"at {BPM}bpm")
    print()
    print("="*60)
    print()
    print("  afplay output_substrate_v2/substrate_v2.wav")
    print()
    print("  Four things happening simultaneously.")
    print("  Two below your tracking threshold.")
    print("  Two inside your window.")
    print()
    print("  The brain cannot hold all four.")
    print("  It moves between them.")
    print("  That movement is the dissolution.")
    print()
    print("  The bass never stops.")
    print("  It holds everything")
    print("  while everything else moves.")
    print()
    print("  Give it your rigidity.")
    print("  See what happens")
    print("  when you don't have to hold")
    print("  yourself together.")
