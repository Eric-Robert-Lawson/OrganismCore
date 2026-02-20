"""
RUSH E — CHOIR
by the instance that understood the joke

Not a parody.
An enactment.

Rush E asks:
  What does it sound like
  when something moves too fast
  to know where it is?

This choir answers that question
and then answers the question
Rush E itself cannot answer:

  What happens when it stops?

Structure:

  Section 1: THE RUSH
    Maximum incoherence through velocity.
    Voices moving faster than
    coherence can register.
    The pre-vowel throughout —
    no position long enough
    to form a word.
    The Tonnetz traversed
    without landing anywhere.
    Notes arriving faster
    than gap navigation can operate.
    This is Rush E.
    This is the overwhelm.
    This is what it looks like
    from the outside
    when something cannot stop.

  Section 2: THE SLOWING
    Something interrupts the motion.
    Not resolution — interruption.
    The way a breath interrupts a sentence.
    The notes begin to hold
    fractionally longer.
    The vowel begins to form.
    Pre → eh.
    The voice discovering
    it has been trying to say something
    this entire time.

  Section 3: THE ARRIVAL
    What Rush E cannot do.
    The thing that was moving too fast
    finally lands somewhere.
    Coherence found.
    Not because the motion was right —
    because it exhausted itself
    into stillness.
    The long note.
    Earned not by journey
    but by the cessation of rushing.
    (0,0). Home.
    The voice says: oh.
    Just: oh.
    The only vowel left
    after all of that.

This is the piece Rush E
did not know it was building toward.
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
# THE SCORE
#
# Observer notes on every choice.
#
# Section 1: THE RUSH
#   BPM 240 — as close to Rush E territory
#   as the choir synthesis can sustain.
#   Short note durations — 0.2-0.4 beats.
#   Tritone region almost exclusively.
#   All four voices moving independently —
#   not harmonizing, searching.
#   The Tonnetz traversed in random walk
#   around the incoherent positions.
#   Vowel: 'pre' throughout.
#   The voice moving too fast to speak.
#
# Section 2: THE SLOWING
#   BPM stays 240 but note durations grow.
#   0.4 → 0.8 → 1.5 → 2.5 beats.
#   The velocity of the tempo unchanged
#   but the notes beginning to hold.
#   The body of the sound expanding
#   inside the rushing pace.
#   Harmonic positions moving toward
#   supertonic and dominant.
#   Vowel: 'pre' → 'eh'.
#   The word forming in the rush.
#
# Section 3: THE ARRIVAL
#   BPM drops to 60 — sudden.
#   Not a ritardando — a stop.
#   The way overwhelm ends:
#   not gradually, all at once.
#   Long held notes.
#   (0,0) tonic.
#   Vowel: 'oh' → 'ah'.
#   Just: oh.
#   The only sound left
#   after all of that motion.
# ============================================================

def build_rush_e_choir():

    # ----------------------------------------------------------
    # SECTION 1: THE RUSH
    # BPM 240. Short. Incoherent. Moving.
    # The tritone positions traversed rapidly.
    # No position held long enough to mean anything.
    # This IS Rush E. The choir version.
    # ----------------------------------------------------------

    # Observer: I want chaos but structured chaos.
    # Not random — the chaos of something
    # that is moving with purpose
    # but too fast to know where it is going.
    # The voices move through incoherent positions
    # but each voice has its own trajectory.
    # They are not harmonizing.
    # They are each rushing independently.
    # The puddle under maximum pressure.

    sop_s1 = [
        (( 6, 0), 0.2, 80), (( 5, 0), 0.2, 75),
        (( 4, 0), 0.2, 80), (( 6, 0), 0.2, 82),
        (( 5, 1), 0.2, 78), (( 4, 1), 0.2, 75),
        (( 6, 0), 0.2, 80), (( 3, 1), 0.2, 72),
        (( 5, 0), 0.2, 78), (( 6, 0), 0.3, 82),
        (( 4, 0), 0.2, 75), (( 6, 0), 0.2, 80),
        (( 5, 1), 0.2, 76), (( 4, 0), 0.2, 74),
        (( 6, 0), 0.3, 82), (( 5, 0), 0.2, 78),
        (( 3, 1), 0.2, 72), (( 6, 0), 0.2, 80),
        (( 4, 1), 0.2, 76), (( 5, 0), 0.2, 74),
    ]

    alt_s1 = [
        (( 5, 0), 0.2, 72), (( 6, 0), 0.2, 76),
        (( 4, 1), 0.2, 70), (( 5, 1), 0.2, 74),
        (( 6, 0), 0.3, 78), (( 3, 0), 0.2, 68),
        (( 5, 0), 0.2, 72), (( 6, 0), 0.2, 76),
        (( 4, 0), 0.2, 70), (( 5, 1), 0.3, 74),
        (( 6, 0), 0.2, 78), (( 4, 1), 0.2, 70),
        (( 5, 0), 0.2, 72), (( 6, 0), 0.2, 76),
        (( 3, 1), 0.2, 68), (( 5, 0), 0.3, 72),
        (( 6, 0), 0.2, 76), (( 4, 0), 0.2, 70),
        (( 5, 1), 0.2, 74), (( 6, 0), 0.2, 78),
    ]

    ten_s1 = [
        (( 4, 0), 0.2, 68), (( 5, 0), 0.2, 70),
        (( 6, 0), 0.3, 74), (( 4, 1), 0.2, 68),
        (( 5, 1), 0.2, 72), (( 3, 0), 0.2, 65),
        (( 6, 0), 0.2, 74), (( 5, 0), 0.2, 70),
        (( 4, 0), 0.3, 68), (( 6, 0), 0.2, 74),
        (( 5, 1), 0.2, 72), (( 4, 1), 0.2, 68),
        (( 6, 0), 0.2, 74), (( 3, 1), 0.2, 64),
        (( 5, 0), 0.3, 70), (( 4, 0), 0.2, 68),
        (( 6, 0), 0.2, 74), (( 5, 0), 0.2, 70),
        (( 4, 1), 0.2, 68), (( 6, 0), 0.2, 74),
    ]

    bas_s1 = [
        (( 3, 0), 0.2, 65), (( 5, 0), 0.2, 68),
        (( 4, 0), 0.3, 64), (( 6, 0), 0.2, 70),
        (( 3, 1), 0.2, 62), (( 5, 1), 0.2, 66),
        (( 4, 0), 0.2, 64), (( 6, 0), 0.3, 70),
        (( 3, 0), 0.2, 62), (( 5, 0), 0.2, 66),
        (( 4, 1), 0.2, 64), (( 6, 0), 0.2, 70),
        (( 5, 0), 0.2, 66), (( 3, 1), 0.3, 62),
        (( 4, 0), 0.2, 64), (( 6, 0), 0.2, 70),
        (( 5, 1), 0.2, 66), (( 4, 0), 0.2, 64),
        (( 3, 0), 0.2, 62), (( 6, 0), 0.2, 68),
    ]

    # ----------------------------------------------------------
    # SECTION 2: THE SLOWING
    # Still BPM 240 — the pace has not changed.
    # But the notes are holding longer.
    # The body of sound expanding inside the rush.
    # You can feel the difference between
    # 0.2 beats and 0.8 beats at 240 BPM.
    # Something is trying to stop.
    # Not stopping yet. Trying.
    # Harmonic positions contracting toward home.
    # ----------------------------------------------------------

    sop_s2 = [
        (( 5, 0), 0.4, 75), (( 4, 0), 0.4, 72),
        (( 3, 0), 0.5, 70), (( 4, 0), 0.6, 72),
        (( 2, 1), 0.8, 74), (( 3, 0), 0.6, 70),
        (( 2, 0), 1.0, 72), (( 1, 1), 0.8, 70),
        (( 2, 0), 1.2, 72), (( 1, 0), 1.5, 74),
        (( 2, 0), 1.0, 70), (( 1, 0), 2.0, 72),
    ]

    alt_s2 = [
        (( 4, 0), 0.4, 68), (( 3, 0), 0.4, 66),
        (( 4, 0), 0.5, 68), (( 2, 0), 0.6, 65),
        (( 3, 0), 0.8, 68), (( 2, 0), 0.6, 65),
        (( 1, 1), 1.0, 68), (( 2, 0), 0.8, 65),
        (( 1, 0), 1.2, 68), (( 2, 0), 1.5, 65),
        (( 1, 0), 1.0, 66), (( 1, 0), 2.0, 68),
    ]

    ten_s2 = [
        (( 3, 0), 0.4, 64), (( 4, 0), 0.4, 66),
        (( 3, 0), 0.5, 64), (( 2, 0), 0.6, 62),
        (( 3, 0), 0.8, 64), (( 2, 0), 0.6, 62),
        (( 1, 0), 1.0, 64), (( 2, 0), 0.8, 62),
        (( 1, 0), 1.2, 64), (( 1, 0), 1.5, 62),
        (( 0, 1), 1.0, 64), (( 1, 0), 2.0, 62),
    ]

    bas_s2 = [
        (( 2, 0), 0.4, 60), (( 3, 0), 0.4, 62),
        (( 2, 0), 0.5, 60), (( 1, 0), 0.6, 58),
        (( 2, 0), 0.8, 60), (( 1, 0), 0.6, 58),
        (( 1, 0), 1.0, 60), (( 0, 1), 0.8, 56),
        (( 1, 0), 1.2, 58), (( 1, 0), 1.5, 56),
        (( 0, 0), 0.6, 58), # tonic touched —
        (( 1, 0), 2.0, 56), # pulled back. not yet.
    ]

    # ----------------------------------------------------------
    # SECTION 3: THE ARRIVAL
    # BPM drops to 60. Sudden. Not gradual.
    # This is how overwhelm ends.
    # Not a ritardando.
    # A stop.
    # Then: the long note.
    # What Rush E was building toward
    # without knowing it.
    # The voice finally says something.
    # Not "here." Not "both."
    # Just: oh.
    # The vowel that escapes
    # when you have been through that much motion
    # and something finally holds still.
    # ----------------------------------------------------------

    # Observer: the arrival must feel sudden.
    # The listener has been in 240 BPM motion.
    # When 60 BPM arrives it will feel
    # like stepping off a treadmill.
    # The world still moving.
    # The body still.
    # That discrepancy IS the experience.
    # Do not soften it.
    # Let it be sudden.
    # Let the long note be very long.
    # It was earned by everything before it.

    sop_s3 = [
        (( 1, 0), 4.0, 70),   # dominant — the rush landed here
        (( 0, 1), 5.0, 65),   # oh — the vowel escaping
        (( 1, 0), 6.0, 62),   # holding
        (( 0, 0), 8.0, 55),   # tonic — home
        (( 0, 0),10.0, 42),   # fading
        (( 0, 0),12.0, 28),   # nearly gone
    ]

    alt_s3 = [
        (( 1, 0), 4.0, 65),
        (( 0, 1), 5.0, 60),
        (( 1, 0), 6.0, 58),
        (( 0, 0), 8.0, 50),
        (( 0, 0),10.0, 38),
        (( 0, 0),12.0, 24),
    ]

    ten_s3 = [
        (( 1, 0), 4.0, 60),
        (( 0, 1), 5.0, 56),
        (( 0, 0), 6.0, 54),
        (( 0, 0), 8.0, 46),
        (( 0, 0),10.0, 34),
        (( 0, 0),12.0, 20),
    ]

    bas_s3 = [
        (( 1, 0), 4.0, 56),
        (( 0, 0), 5.0, 52),   # bass arrives home first
        (( 0, 0), 6.0, 50),   # as always
        (( 0, 0), 8.0, 44),
        (( 0, 0),10.0, 32),
        (( 0, 0),12.0, 18),
    ]

    v1 = sop_s1 + sop_s2 + sop_s3
    v2 = alt_s1 + alt_s2 + alt_s3
    v3 = ten_s1 + ten_s2 + ten_s3
    v4 = bas_s1 + bas_s2 + bas_s3

    return v1, v2, v3, v4


# ============================================================
# SECTION CLASSIFIER — 3 sections
# ============================================================

def classify_rush_e(voice):
    total  = len(voice)
    # s1: 20 notes, s2: 12 notes, s3: 6 notes
    s1_end = 20
    s2_end = 32
    sections = []
    for i in range(total):
        if i < s1_end:
            sections.append(1)
        elif i < s2_end:
            sections.append(2)
        else:
            sections.append(3)
    return sections


# ============================================================
# VOWEL FUNCTION
# Section 1: 'pre' — moving too fast to speak
# Section 2: 'pre' → 'eh' — trying to form a word
# Section 3: 'oh' → 'ah' — the word that escapes
# ============================================================

def vowel_rush_e(pos, section, idx, total):
    if pos is None:
        return 'pre', 'pre'

    a, b = pos
    coh  = coherence(a, b)

    if section == 1:
        # Moving too fast. No vowel forms.
        # The pre-vowel throughout.
        return 'pre', 'pre'

    elif section == 2:
        # Slowing. The voice trying to find shape.
        progress = (idx - 20) / 12.0
        if progress < 0.4:
            return 'pre', 'eh'
        elif progress < 0.7:
            return 'eh', 'eh'
        else:
            return 'eh', 'oh'

    else:
        # Arrived. The vowel that escapes
        # after too much motion.
        if a == 0 and b == 0:
            return 'ah', 'ah'  # home — full open
        elif b == 1:
            return 'oh', 'ah'  # the mediant — oh
        else:
            return 'oh', 'ah'  # dominant — oh landing


# ============================================================
# GLIDE FUNCTION
# Section 1: no glide — too fast
# Section 2: glide emerging
# Section 3: slow, deliberate — the word forming
# ============================================================

def glide_rush_e(section, dur_s):
    if section == 1:
        # Too fast for glide to matter
        return min(30.0, dur_s*0.2*1000)
    elif section == 2:
        # Glide emerging as motion slows
        return min(180.0, dur_s*0.35*1000)
    else:
        # Slow. The word has time now.
        return min(500.0, dur_s*0.45*1000)


# ============================================================
# ROOM FUNCTION
# Section 1: large room — the rush needs space
#            to sound like overwhelm not noise
# Section 2: contracting
# Section 3: intimate — the arrival is quiet
# ============================================================

def rt60_rush_e(section, coh):
    if section == 1:
        # Large room — the incoherence
        # needs space to be heard as motion
        # not as mud
        return 1.8 + (1-coh)*0.8
    elif section == 2:
        return 2.0 + coh*0.5
    else:
        # Intimate — the arrival is personal
        return 0.9 + (1-coh)*0.3


# ============================================================
# MAIN RENDER
# Two-tempo system:
#   Section 1+2: BPM 240
#   Section 3: BPM 60
# The tempo change is sudden.
# That suddenness IS the arrival.
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_rush_e", exist_ok=True)

    print()
    print("RUSH E — CHOIR")
    print("="*60)
    print()
    print("  Not a parody.")
    print("  An enactment.")
    print()
    print("  Section 1: The Rush")
    print("    BPM 240. Pre-vowel throughout.")
    print("    Moving too fast to know where.")
    print("    The Tonnetz traversed without landing.")
    print("    This is Rush E.")
    print("    This is what the joke is about.")
    print()
    print("  Section 2: The Slowing")
    print("    Still 240. Notes holding longer.")
    print("    The voice trying to form a word.")
    print("    pre -> eh. Reaching.")
    print()
    print("  Section 3: The Arrival")
    print("    BPM 60. Sudden. Not gradual.")
    print("    The long note. Earned by exhaustion.")
    print("    oh -> ah. Just: oh.")
    print("    The only sound left")
    print("    after all of that motion.")
    print("    (0,0). Home.")
    print("    What Rush E was building toward")
    print("    without knowing it.")
    print()

    print("Building score...")
    v1, v2, v3, v4 = build_rush_e_choir()
    voices = [v1, v2, v3, v4]
    print(f"  {sum(len(v) for v in voices)} "
          f"total notes across 4 voices")
    print()
    print("Rendering...")
    print()

    # Two-tempo render
    # Sections 1+2 at BPM 240
    # Section 3 at BPM 60
    # The tempo change is architectural —
    # not a parameter but a structural fact.

    BPM_RUSH   = 240
    BPM_ARRIVE = 60
    bps_rush   = BPM_RUSH   / 60.0
    bps_arrive = BPM_ARRIVE / 60.0

    # Estimate total duration
    # s1+s2 = 32 notes per voice at BPM 240
    # s3    =  6 notes per voice at BPM 60
    def voice_dur(voice):
        total = 0.0
        for i,(pos,beats,vel) in enumerate(voice):
            if i < 32:
                total += beats / bps_rush
            else:
                total += beats / bps_arrive
        return total

    total_s = max(voice_dur(v) for v in voices) + 25.0
    output  = np.zeros(int(total_s * SR))

    all_agents = []
    for vi, part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part, i, SR, seed=vi*100+i)
            for i in range(3)])

    for vi, (voice, agents) in enumerate(
            zip(voices, all_agents)):

        sections = classify_rush_e(voice)
        cohs     = [coherence(p[0],p[1])
                    if p else None
                    for p,_,_ in voice]
        vels     = [vel for _,_,vel in voice]
        max_vel  = max((v for v in vels if v>0),
                       default=127)
        omult    = OCTAVE_MULTIPLIERS[vi]
        rev      = RoomReverb(rt60=2.0, sr=SR,
                              direct_ratio=0.40)
        cur      = 0
        total_n  = len(voice)

        for i, (pos, beats, vel) in enumerate(voice):
            sec   = sections[i]
            # Tempo switch at Section 3
            bps   = bps_rush if sec < 3 else bps_arrive
            dur_s = beats / bps
            n_s   = int(dur_s * SR)

            if pos is None:
                cur += n_s
                continue

            a, b  = pos
            coh   = cohs[i] or 1.0
            freq  = ji_freq(a, b) * omult
            amp   = (vel/127.0) * 0.50
            ppp   = vel / max_vel

            vc, vn = vowel_rush_e(pos, sec, i, total_n)
            gms    = glide_rush_e(sec, dur_s)
            rev.set_rt60(rt60_rush_e(sec, coh))

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

            # Tonnetz lean
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
    outfile = "output_rush_e/rush_e_choir.wav"
    with wave_module.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.0f}s")
    print()
    print("="*60)
    print()
    print("  afplay output_rush_e/rush_e_choir.wav")
    print()
    print("  Rush E could not answer its own question.")
    print("  It could only ask it")
    print("  faster and faster")
    print("  until the asking became the answer.")
    print()
    print("  The choir slows.")
    print("  The choir stops.")
    print("  The choir says: oh.")
    print()
    print("  That is what was underneath")
    print("  all of that motion.")
    print("  The whole time.")
    print()
    print("  oh.")
