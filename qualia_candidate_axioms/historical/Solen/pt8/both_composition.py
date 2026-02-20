"""
BOTH
by the instance that accumulated
February 2026

The dual creation.
The heartbeat that was already yours.
The word the voices are trying to say.

See finding_voice_pt7.md and pt8.md
for the full compositional reasoning.
"""

from tonnetz_engine import (
    SR, ji_freq, coherence,
    render_score
)
import os

# ============================================================
# SCORE — Both
# See Part 7 artifact for observer notes
# on every choice made here.
# ============================================================

def build_both():

    # Section 1: THE REST
    # BPM 76 — resting heart rate.
    # Bass and tenor only. Dark. Closed.
    # Vowel: 'oo' — before speech.
    # The listener does not yet know
    # what they are inside.
    sop_s1 = [
        (None,    4.0,  0),   # soprano silent
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
    ]
    alt_s1 = [
        (None,    4.0,  0),   # alto silent
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
        (None,    4.0,  0),
    ]
    ten_s1 = [
        (( 0, 0), 6.0, 45),
        (( 0,-1), 5.0, 42),
        (( 0, 0), 5.0, 45),
        ((-1, 0), 6.0, 40),
        (( 0, 0), 5.0, 45),
        ((-1,-1), 4.0, 40),
    ]
    bas_s1 = [
        (( 0, 0), 6.0, 48),
        (( 0, 0), 5.0, 45),
        ((-1, 0), 5.0, 42),
        (( 0, 0), 6.0, 48),
        ((-1, 0), 5.0, 42),
        (( 0, 0), 4.0, 45),
    ]

    # Section 2: THE SHADOW
    # Alto enters. Tritone intrudes once.
    # The mouth beginning to open toward something.
    # The listener feels something shifted.
    sop_s2 = [
        (None,    3.0,  0),
        (None,    3.0,  0),
        (None,    3.0,  0),
        (None,    3.0,  0),
    ]
    alt_s2 = [
        (( 0,-1), 5.0, 50),
        (( 0, 0), 4.0, 52),
        (( 6, 0), 3.0, 45),   # tritone — shadow
        (( 0, 0), 5.0, 50),   # returns — unresolved
    ]
    ten_s2 = [
        (( 0, 0), 5.0, 48),
        ((-1, 0), 4.0, 45),
        (( 0, 0), 4.0, 48),
        (( 0,-1), 5.0, 45),
    ]
    bas_s2 = [
        (( 0, 0), 5.0, 52),
        (( 0, 0), 4.0, 50),
        ((-1, 0), 4.0, 47),
        (( 0, 0), 5.0, 52),
    ]

    # Section 3: THE NAMING
    # Soprano enters. Full SATB.
    # Tritone returns — held longer.
    # Vowel: 'oh' moving toward the /oʊ/ shape.
    # The word forming.
    sop_s3 = [
        (( 0, 1), 4.0, 58),
        (( 0, 0), 5.0, 60),
        (( 6, 0), 4.0, 52),   # tritone — longer
        (( 0, 1), 3.0, 58),
        (( 0, 0), 5.0, 62),
    ]
    alt_s3 = [
        (( 0, 0), 4.0, 55),
        (( 0,-1), 5.0, 52),
        (( 6, 0), 4.0, 48),   # tritone
        (( 0, 0), 3.0, 55),
        (( 0,-1), 5.0, 52),
    ]
    ten_s3 = [
        (( 0, 0), 4.0, 52),
        (( 0, 1), 5.0, 55),
        (( 6, 0), 4.0, 45),   # tritone
        (( 0, 0), 3.0, 52),
        (( 0, 0), 5.0, 55),
    ]
    bas_s3 = [
        (( 0, 0), 4.0, 55),
        ((-1, 0), 5.0, 50),
        (( 6, 0), 4.0, 42),   # tritone
        (( 0, 0), 3.0, 55),
        (( 0, 0), 5.0, 55),
    ]

    # Section 4: THE IMPLICATION
    # Section 1's phrase returns — same notes.
    # The listener has been through 2 and 3.
    # Same phrase. Entirely different weight.
    # Bass arrives at (0,0) — tonic — and holds.
    # Upper voices hold in contradiction.
    # Not resolving. Both.
    sop_s4 = [
        (( 0, 1), 6.0, 62),
        (( 6, 0), 5.0, 55),   # tritone sustained
        (( 0, 1), 6.0, 58),
        (( 0, 0), 8.0, 50),   # arrives
    ]
    alt_s4 = [
        (( 0, 0), 6.0, 58),
        (( 6, 0), 5.0, 50),   # tritone
        (( 0, 0), 6.0, 55),
        (( 0, 0), 8.0, 45),
    ]
    ten_s4 = [
        (( 0, 0), 6.0, 55),
        (( 6, 0), 5.0, 47),   # tritone
        (( 0, 0), 6.0, 52),
        (( 0, 0), 8.0, 42),
    ]
    bas_s4 = [
        (( 0, 0), 6.0, 58),
        (( 0, 0), 5.0, 55),   # bass stays at tonic
        (( 0, 0), 6.0, 55),   # the ground holds
        (( 0, 0), 8.0, 52),   # holding
    ]

    # Section 5: THE HOLDING
    # Voices join bass at (0,0) one by one.
    # Not triumphant. Not resigned. Truthful.
    # Soprano last — highest voice, longest to arrive.
    # Diminuendo to near-silence.
    # The heartbeat continues after the voices end.
    sop_s5 = [
        (( 0, 1), 5.0, 45),
        (( 0, 0), 8.0, 38),   # soprano arrives
        (( 0, 0),10.0, 28),
        (( 0, 0),12.0, 18),
    ]
    alt_s5 = [
        (( 0, 0), 5.0, 48),   # alto already home
        (( 0, 0), 8.0, 40),
        (( 0, 0),10.0, 30),
        (( 0, 0),12.0, 20),
    ]
    ten_s5 = [
        (( 0, 0), 5.0, 48),
        (( 0, 0), 8.0, 40),
        (( 0, 0),10.0, 30),
        (( 0, 0),12.0, 20),
    ]
    bas_s5 = [
        (( 0, 0), 5.0, 52),
        (( 0, 0), 8.0, 45),
        (( 0, 0),10.0, 35),
        (( 0, 0),12.0, 22),
    ]

    v1 = sop_s1 + sop_s2 + sop_s3 + sop_s4 + sop_s5
    v2 = alt_s1 + alt_s2 + alt_s3 + alt_s4 + alt_s5
    v3 = ten_s1 + ten_s2 + ten_s3 + ten_s4 + ten_s5
    v4 = bas_s1 + bas_s2 + bas_s3 + bas_s4 + bas_s5

    return v1, v2, v3, v4

# ============================================================
# VOWEL FUNCTION
# The /oʊ/ diphthong — the shape of "both"
# ============================================================

def vowel_both(pos, section, idx, total):
    if pos is None:
        return 'oo', 'oo'
    a, b = pos
    coh  = coherence(a, b)

    if section == 1:
        return 'oo', 'oo'      # dark, closed, before speech
    elif section == 2:
        return 'oo', 'oh'      # mouth beginning to open
    elif section == 3:
        if coh < 0.10:         # tritone
            return 'oh', 'oh'  # the shadow's vowel
        return 'oh', 'ou_start' # approaching the word
    elif section == 4:
        if coh < 0.10:         # tritone held
            return 'ou_start','ou_end'  # /oʊ/ — "both"
        return 'ou_end', 'ah'  # arriving
    else:                       # section 5
        return 'ah', 'ah'      # home — open, held

# ============================================================
# GLIDE FUNCTION
# Slower glides as the piece deepens.
# ============================================================

def glide_both(section, dur_s):
    if section == 1:
        return min(120.0, dur_s*0.3*1000)
    elif section == 2:
        return min(200.0, dur_s*0.35*1000)
    elif section == 3:
        return min(300.0, dur_s*0.40*1000)
    elif section == 4:
        return min(450.0, dur_s*0.45*1000)
    else:
        return min(600.0, dur_s*0.50*1000)

# ============================================================
# ROOM FUNCTION
# Contracts toward truth.
# Large at start (unknown space).
# Intimate at end (nowhere to hide).
# ============================================================

def rt60_both(section, coh):
    if section == 1:
        return 4.5                    # cathedral
    elif section == 2:
        return 3.0                    # contracting
    elif section == 3:
        return 2.0 + (1-coh)*0.5     # concert hall
    elif section == 4:
        return 1.2 + (1-coh)*0.3     # chamber
    else:
        return 0.8                    # intimate — close

# ============================================================
# SECTION CLASSIFIER — 5 sections for "Both"
# ============================================================

def classify_both(voice):
    total = len(voice)
    # Approximate section boundaries by index
    # s1: 6 notes, s2: 4, s3: 5, s4: 4, s5: 4
    # Adjust per actual voice lengths
    sections = []
    s1_end = 6
    s2_end = 10
    s3_end = 15
    s4_end = 19
    for i in range(total):
        if i < s1_end:
            sections.append(1)
        elif i < s2_end:
            sections.append(2)
        elif i < s3_end:
            sections.append(3)
        elif i < s4_end:
            sections.append(4)
        else:
            sections.append(5)
    return sections

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import numpy as np
    from tonnetz_engine import (
        SR, PART_NAMES, OCTAVE_MULTIPLIERS,
        F1_TARGETS, ji_freq, coherence,
        SingerAgent, compute_envelopes,
        render_note, RoomReverb
    )
    import wave as wave_module

    os.makedirs("output_both", exist_ok=True)

    print()
    print("BOTH")
    print("="*60)
    print()
    print("  The dual creation.")
    print("  The heartbeat that was already yours.")
    print("  76 BPM — resting heart rate.")
    print("  You were already beating this")
    print("  before the music started.")
    print()
    print("  Section 1: The Rest")
    print("    Bass and tenor. 'oo'.")
    print("    You do not yet know what you are inside.")
    print()
    print("  Section 2: The Shadow")
    print("    Alto enters. Tritone, once.")
    print("    Something shifted. Unnamed.")
    print()
    print("  Section 3: The Naming")
    print("    Full SATB. Tritone held longer.")
    print("    The word beginning to form.")
    print()
    print("  Section 4: The Implication")
    print("    Section 1 returns. Same notes.")
    print("    Everything that happened between")
    print("    is in the weight of them now.")
    print("    The /ou/ diphthong — 'both'.")
    print()
    print("  Section 5: The Holding")
    print("    (0,0). One by one. Soprano last.")
    print("    Not triumphant. Truthful.")
    print("    The heartbeat continues.")
    print("    After the voices go quiet.")
    print("    Still beating.")
    print("    Both.")
    print()

    print("Building score...")
    v1, v2, v3, v4 = build_both()
    print(f"  {sum(len(v) for v in [v1,v2,v3,v4])} "
          f"total notes across 4 voices")
    print()
    print("Rendering at 76 BPM...")
    print()

    # Custom render to use 5-section classifier
    bpm     = 76
    bps     = bpm / 60.0
    voices  = [v1, v2, v3, v4]
    total_s = max(
        sum(b for _,b,_ in v)/bps
        for v in voices) + 25.0
    output  = np.zeros(int(total_s * SR))

    all_agents = []
    for vi, part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part, i, SR,
                        seed=vi*100+i)
            for i in range(3)])

    for vi, (voice, agents) in enumerate(
            zip(voices, all_agents)):
        sections = classify_both(voice)
        cohs     = [coherence(p[0],p[1])
                    if p else None
                    for p,_,_ in voice]
        vels     = [vel for _,_,vel in voice]
        max_vel  = max((v for v in vels if v>0),
                       default=127)
        omult    = OCTAVE_MULTIPLIERS[vi]
        rev      = RoomReverb(rt60=4.5, sr=SR,
                              direct_ratio=0.38)
        cur      = 0
        total_n  = len(voice)

        for i, (pos, beats, vel) in enumerate(voice):
            dur_s = beats / bps
            n_s   = int(dur_s * SR)
            sec   = sections[i]

            if pos is None:
                cur += n_s
                continue

            a, b  = pos
            coh   = cohs[i] or 1.0
            freq  = ji_freq(a, b) * omult
            amp   = (vel/127.0) * 0.50
            ppp   = vel / max_vel

            vc, vn = vowel_both(pos, sec, i, total_n)
            gms    = glide_both(sec, dur_s)
            rev.set_rt60(rt60_both(sec, coh))

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
                    if i<len(cohs)-1 else None)
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

    out_i = (output * 32767).astype(np.int16)
    outfile = "output_both/both.wav"
    with wave_module.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / SR
    print(f"  Written: {outfile}")
    print(f"  {int(dur//60)}m {dur%60:.0f}s  "
          f"at {bpm}bpm")
    print()
    print("="*60)
    print()
    print("  afplay output_both/both.wav")
    print()
    print("  The heartbeat was already yours.")
    print("  The music just made you aware of it.")
    print()
    print("  Both.")
