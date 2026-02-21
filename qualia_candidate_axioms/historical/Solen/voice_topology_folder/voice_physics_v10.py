"""
VOICE PHYSICS v10
February 2026

ONSET FIXES — driven by onset_diagnostic.py.

The onset diagnostic measures the first 20ms
of each problem phoneme and reports:
  - spectral centroid
  - periodicity
  - peak prominence
  - F1-band energy ratio
  - sibilant onset timing vs vowel departure

v9 fixed levels and durations.
v10 fixes the SHAPE of consonant onsets.

The four remaining artifacts and their
onset diagnostic signatures:

  "ea-the":
    DH onset periodicity > 0.40.
    DH onset centroid < 1800Hz.
    Glottal pulse at F1=270Hz from t=0.
    → FIX A: DH voiced source FADES IN.
      First 25ms: zero voiced, bypass only.
      Voiced rises linearly 0→fraction
      over the phoneme body.
      The dental friction IS the onset.
      The voiced buzz grows into the body.

  "CH-here":
    H onset peak_prominence > 3.0.
    Aspiration noise resonated by
    IH formants at F2=1990Hz from t=0.
    → FIX B: H aspiration uses NEUTRAL
      formant target for first 30ms.
      F target blends from neutral
      toward IH over the H duration.
      Aspiration shaped to mid-range,
      not palatal, at onset.
      The palatal character emerges
      at the vowel onset, not the H onset.

  "dragged S/Z":
    Sibilance rises before F1 has departed.
    → FIX C: Sibilant onset delay now uses
      the MEASURED F1 departure time
      as its reference, not a fixed sample count.
      In practice: delay = n_on (full transition),
      not n_on // 2.
      The bypass starts ONLY after the
      full n_on transition has elapsed.
      No overlap between vowel formants
      and sibilance.

These three fixes are surgical.
They do not change the steady-state
character of any phoneme.
They change only the first 20-30ms.

Import chain:
  v10 → v9 → v8 → v7 → v6 → v5 → v4 → v3
"""

from voice_physics_v9 import (
    tract,
    warm,
    resonator,
    breath_rest,
    VOWEL_F, GAINS,
    WORD_SYLLABLES,
    get_f, get_b, scalar,
    safe_bp, safe_lp, safe_hp,
    apply_room, write_wav,
    TARGET_RMS, calibrate, rms,
    PITCH, DIL, SR, DTYPE, f32,
    TRANS_MS, DEFAULT_TRANS_MS,
    trans_n,
    REST_MAX_MS,
    NEUTRAL_F, NEUTRAL_B,
    VOICED_TRACT_FRACTION,
    Z_VOICED_TRACT, ZH_VOICED_TRACT,
    V_VOICED_TRACT,
    VOWEL_PHONEMES, DIPHTHONG_PHONEMES,
    VOWEL_MAX_MS, DIPHTHONG_MAX_MS,
    APPROX_MAX_MS, FRIC_MAX_MS,
    FINAL_FRIC_MAX_MS,
    DH_MAX_MS, H_MAX_MS,
    H_ASPIRATION_GAIN,
    build_trajectories,
    ph_spec_v9,
    plan_prosody,
    get_calibrated_gains_v8,
    recalibrate_gains_v8,
    RESONATOR_CFG, BROADBAND_CFG,
    cavity_resonator,
    VOICED_FRICS, FRIC_VOICED_TRACT,
)
import numpy as np
from scipy.signal import lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# FIX A: DH VOICED SOURCE FADE-IN
#
# v9: voiced at DH_VOICED_FRACTION from t=0.
#     First sample has full-fraction voiced buzz.
#     Glottal pulse through F1=270Hz = "ea" prefix.
#
# v10: voiced component fades IN over DH body.
#      First DH_VOICED_FADE_MS: bypass only.
#      Then voiced rises 0 → DH_VOICED_FRACTION.
#      The dental friction is the onset.
#      The voiced buzz grows into the body.
#      The ear hears: dental → dental+buzz.
#      Not: buzz+dental → dental+buzz.
# ============================================================

DH_VOICED_FRACTION  = 0.30   # inherited from v9
DH_VOICED_FADE_MS   = 25     # ms before voiced starts
# After DH_VOICED_FADE_MS, voiced rises linearly
# from 0 to DH_VOICED_FRACTION over the
# remaining phoneme body.


# ============================================================
# FIX B: H ASPIRATION WITH NEUTRAL ONSET
#
# v9: H aspiration through next-vowel formants
#     from t=0.
#     IH F2=1990Hz peak at onset = "CH" prefix.
#
# v10: H aspiration through NEUTRAL formants
#      for first H_NEUTRAL_MS.
#      Then formants blend toward next-vowel
#      target over remaining H duration.
#      The aspiration sounds pharyngeal at onset.
#      It sounds like the approaching vowel
#      only near the vowel boundary.
#
# Neutral aspiration formants:
#   These are laryngeal/pharyngeal in character.
#   Lower F2 = less palatal = less "CH"-like.
# ============================================================

H_NEUTRAL_MS      = 30      # ms at neutral formants
H_NEUTRAL_F       = [450, 1100, 2500, 3400]
# F1=450: slightly open throat
# F2=1100: pharyngeal, not palatal
# (vs IH F2=1990 which sounds palatal)
# F3=2500, F4=3400: neutral


# ============================================================
# FIX C: FULL TRANSITION DELAY FOR SIBILANT BYPASS
#
# v9: bypass onset delay = n_on // 2
#     (half the transition)
#     Still overlaps with vowel formants.
#
# v10: bypass onset delay = n_on
#      (full transition)
#      The bypass starts ONLY after the
#      tract has completed its move
#      from vowel to fricative position.
#      No overlap. No smear.
# ============================================================

# This is applied in build_source_and_bypass_v10.
# The onset_delay for fricative bypass = n_on
# (vs n_on//2 in v9).


# ============================================================
# BYPASS GENERATOR v10
# Identical to v9 but accepts onset_delay
# as full n_on (not half).
# (No code change needed — just passes
#  different onset_delay value.)
# ============================================================

def make_bypass_v10(ph, n_s, sr=SR,
                     next_is_vowel=False,
                     onset_delay=0):
    """
    v10 bypass generator.
    Identical logic to v9 make_bypass_v9.
    onset_delay is now the FULL n_on
    transition duration (not half).
    """
    from voice_physics_v9 import make_bypass_v9
    return make_bypass_v9(
        ph, n_s, sr=sr,
        next_is_vowel=next_is_vowel,
        onset_delay=onset_delay)


# ============================================================
# MODIFIED TRAJECTORY BUILDER v10
#
# FIX B requires a modified H trajectory:
# the first H_NEUTRAL_MS of H uses
# H_NEUTRAL_F formants, then blends
# toward the next-vowel target.
#
# This is done by overriding the F_tgt
# for H phonemes in a post-process step
# applied to the F_full arrays.
# ============================================================

def build_trajectories_v10(phoneme_specs, sr=SR):
    """
    v10 trajectory builder.

    FIX B: After the standard trajectory
    is built for H phonemes, the first
    H_NEUTRAL_MS of the H formant arrays
    are replaced with a blend from
    F_current (previous phoneme end)
    toward H_NEUTRAL_F, then from
    H_NEUTRAL_F toward the next-vowel target.

    This makes H aspiration start
    with a neutral pharyngeal character
    rather than immediately coarticulating
    to the following palatal vowel.
    """
    # First: build standard trajectories
    F_full, B_full, seg_ends = \
        build_trajectories(
            phoneme_specs, sr=sr)

    n_neutral = int(H_NEUTRAL_MS / 1000.0 * sr)

    # Post-process H phoneme segments
    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s = spec['n_s']
        ph  = spec['ph']

        if ph == 'H':
            # How long to blend from neutral
            n_neu = min(n_neutral, n_s * 2 // 3)

            # What the formants were at H onset
            # (end of previous phoneme = pos-1)
            if pos > 0:
                F_prev = [float(
                    F_full[fi][pos-1])
                    for fi in range(4)]
            else:
                F_prev = list(NEUTRAL_F)

            # What the formants are at H end
            # (start of next phoneme)
            F_end_h = [float(
                F_full[fi][pos + n_s - 1])
                for fi in range(4)]

            for fi in range(4):
                f_arr = F_full[fi][pos:pos+n_s].copy()

                if n_neu > 0 and n_neu < n_s:
                    # Phase 1: F_prev → H_NEUTRAL_F
                    # over first n_neu samples
                    phase1 = np.linspace(
                        F_prev[fi],
                        H_NEUTRAL_F[fi],
                        n_neu, dtype=DTYPE)
                    f_arr[:n_neu] = phase1

                    # Phase 2: H_NEUTRAL_F → F_end_h
                    # over remaining samples
                    n_phase2 = n_s - n_neu
                    if n_phase2 > 0:
                        phase2 = np.linspace(
                            H_NEUTRAL_F[fi],
                            F_end_h[fi],
                            n_phase2, dtype=DTYPE)
                        f_arr[n_neu:] = phase2

                elif n_neu >= n_s:
                    # Short H: all neutral blend
                    f_arr[:] = np.linspace(
                        F_prev[fi],
                        H_NEUTRAL_F[fi],
                        n_s, dtype=DTYPE)

                F_full[fi][pos:pos+n_s] = f_arr

        pos += n_s

    return F_full, B_full, seg_ends


# ============================================================
# SOURCE BUILDER v10
#
# FIX A: DH voiced fade-in.
# FIX C: Full n_on delay for sibilant bypass.
# H source unchanged from v9 (pure aspiration).
# ============================================================

def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v10 source builder.
    FIX A: DH voiced component fades in
           over DH_VOICED_FADE_MS from zero.
    FIX C: Fricative bypass onset delay = n_on
           (full transition, not half).
    H: pure aspiration unchanged from v9.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # F0 and oq trajectories
    f0_traj = np.zeros(n_total, dtype=DTYPE)
    oq_traj = np.zeros(n_total, dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s     = spec['n_s']
        f0_this = spec.get('pitch', PITCH)
        oq_this = spec.get('oq', 0.65)
        f0_next = (phoneme_specs[si+1]
                   .get('pitch', PITCH)
                   if si < len(phoneme_specs)-1
                   else f0_this)
        oq_next = (phoneme_specs[si+1]
                   .get('oq', 0.65)
                   if si < len(phoneme_specs)-1
                   else oq_this)
        f0_traj[pos:pos+n_s] = np.linspace(
            f0_this, f0_next, n_s)
        oq_traj[pos:pos+n_s] = np.linspace(
            oq_this, oq_next, n_s)
        pos += n_s

    # Rosenberg pulse voiced source
    T     = 1.0/sr
    raw_v = np.zeros(n_total, dtype=DTYPE)
    p     = 0.0
    for i in range(n_total):
        f0  = float(f0_traj[i])
        oq_ = max(0.40, min(0.85,
                  float(oq_traj[i])))
        p  += f0*(1+np.random.normal(
            0, 0.005))*T
        if p >= 1.0: p -= 1.0
        raw_v[i] = (
            (p/oq_)*(2-p/oq_) if p < oq_
            else 1-(p-oq_)/(1-oq_+1e-9))
    raw_v = f32(np.diff(
        raw_v, prepend=raw_v[0]))
    try:
        b, a  = safe_lp(20, sr)
        sh_   = f32(np.random.normal(
            0, 1, n_total))
        sh_   = f32(lfilter(b, a, sh_))
        sh_   = f32(np.clip(
            1+0.030*sh_, 0.4, 1.6))
        raw_v = raw_v * sh_
    except:
        pass
    asp_src = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b, a    = safe_bp(400, 2200, sr)
        asp_src = f32(lfilter(b, a, asp_src))
    except:
        asp_src = f32(np.zeros(n_total))
    raw_v       = raw_v + asp_src
    voiced_full = calibrate(raw_v)

    # Aspiration noise source (for H)
    asp_noise = calibrate(
        f32(np.random.normal(0, 1, n_total)))
    try:
        b, a      = safe_bp(200, 7000, sr)
        asp_noise = f32(lfilter(b, a, asp_noise))
        asp_noise = calibrate(asp_noise)
    except:
        pass

    noise_full = calibrate(
        f32(np.random.normal(0, 1, n_total)))

    VOWELS_AND_APPROX = set(
        'AA AE AH AO AW AY EH ER IH IY '
        'OH OW OY UH UW L R W Y M N NG'.split())

    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []

    n_dh_fade = int(DH_VOICED_FADE_MS
                     / 1000.0 * sr)

    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source', 'voiced')
        s = pos
        e = pos + n_s

        next_ph = (phoneme_specs[si+1]['ph']
                   if si < len(phoneme_specs)-1
                   else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        # Transition zone
        n_on  = min(trans_n(ph, sr), n_s // 3)
        n_off = min(trans_n(ph, sr), n_s // 3)
        n_body = n_s - n_on - n_off

        if stype == 'voiced':
            tract_source[s:e] = \
                voiced_full[s:e]

        elif stype == 'h':
            # Pure aspiration — unchanged from v9.
            # Formant shaping is handled by
            # build_trajectories_v10 (FIX B).
            n_asp = max(
                int(n_s * 0.30),
                min(int(0.025*sr), n_s))
            asp_env = np.ones(n_s, dtype=DTYPE)
            n_fi = min(int(0.008*sr), n_s//4)
            if n_fi > 0:
                asp_env[:n_fi] = np.linspace(
                    0.3, 1.0, n_fi)
            n_fo = min(int(0.012*sr), n_s//4)
            if n_fo > 0:
                asp_env[-n_fo:] = np.linspace(
                    1.0, 0.0, n_fo)
            tract_source[s:e] = (
                asp_noise[s:e] *
                f32(asp_env) *
                H_ASPIRATION_GAIN)

        elif stype == 'dh':
            # FIX A: voiced fades IN.
            # First n_dh_fade: zero voiced.
            # Then rises 0 → DH_VOICED_FRACTION
            # over remaining body.
            vf     = DH_VOICED_FRACTION
            n_fade = min(n_dh_fade, n_s)
            n_rise = n_s - n_fade

            voiced_amp = np.zeros(n_s, dtype=DTYPE)
            if n_rise > 0:
                voiced_amp[n_fade:] = f32(
                    np.linspace(0.0, vf, n_rise))

            # Also fade out over n_off zone
            # (from v9 fix C)
            if n_off > 0 and n_body > 0:
                fade_start = n_on + n_body
                voiced_amp[fade_start:] = f32(
                    np.linspace(
                        float(voiced_amp[
                            min(fade_start,
                                n_s-1)]),
                        0.0, n_off))

            tract_source[s:e] = \
                voiced_full[s:e] * \
                f32(voiced_amp)

            # FIX C: bypass onset = full n_on
            onset_delay = n_on
            byp = make_bypass_v10(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=onset_delay)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                vf  = FRIC_VOICED_TRACT.get(
                    ph, VOICED_TRACT_FRACTION)
                amp = np.ones(n_s, dtype=DTYPE)
                fade_start = n_on + n_body
                if n_off > 0 and n_body >= 0:
                    amp[fade_start:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(amp) * vf

            # FIX C: full n_on delay
            onset_delay = n_on
            byp = make_bypass_v10(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=onset_delay)
            bypass_segs.append((s, byp))

        elif stype in ('stop_unvoiced',
                        'stop_voiced'):
            clos_n  = spec.get('clos_n',  0)
            burst_n = spec.get('burst_n', 0)
            vot_n   = spec.get('vot_n',   0)
            bamp    = spec.get(
                'burst_amp', 0.28)
            bhp     = spec.get(
                'burst_hp', 2000)
            is_vcd  = (stype == 'stop_voiced')

            if is_vcd and clos_n > 0:
                tract_source[s:s+clos_n] = \
                    voiced_full[s:s+clos_n] \
                    * 0.055
            if burst_n > 0:
                bs = clos_n
                be = bs + burst_n
                if be <= n_s:
                    burst = noise_full[
                        s+bs:s+be].copy()
                    try:
                        b, a = safe_hp(bhp, sr)
                        burst = f32(
                            lfilter(b, a, burst))
                    except:
                        pass
                    benv = f32(np.exp(
                        -np.arange(burst_n) /
                        burst_n * 20))
                    tract_source[s+bs:s+be] = \
                        burst * benv * bamp
            vot_s = clos_n + burst_n
            vot_e = vot_s  + vot_n
            if vot_n > 0 and vot_e <= n_s:
                ne2 = f32(np.linspace(
                    1, 0, vot_n))
                ve2 = 1.0 - ne2
                tract_source[
                    s+vot_s:s+vot_e] = (
                    noise_full[
                        s+vot_s:s+vot_e]*ne2 +
                    voiced_full[
                        s+vot_s:s+vot_e]*ve2)
            tr_s = vot_e
            if tr_s < n_s:
                tract_source[s+tr_s:e] = \
                    voiced_full[s+tr_s:e]

        pos += n_s

    return f32(tract_source), bypass_segs


# ============================================================
# PHRASE SYNTHESIS v10
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v10: Onset fixes.
      FIX A: DH voiced fades in over 25ms.
      FIX B: H aspiration starts neutral,
             blends to next-vowel formants.
      FIX C: Sibilant bypass starts after
             FULL n_on transition.
    """
    prosody = plan_prosody(
        words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch_base,
        dil=dil)

    if not prosody:
        return f32(np.zeros(int(0.1*sr)))

    n_items = len(prosody)
    specs   = []
    for i, item in enumerate(prosody):
        ph         = item['ph']
        dur_ms     = item['dur_ms']
        pitch_     = pitch_base * item['f0_mult']
        oq_        = item['oq']
        bw_m       = item['bw_mult']
        amp_       = item['amp']
        rest_ms    = item.get('rest_ms', 0.0)
        word_final = item.get('word_final', False)
        next_ph    = (prosody[i+1]['ph']
                      if i < n_items-1
                      else None)
        spec = ph_spec_v9(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)
        specs.append(spec)

    # FIX B: modified trajectory builder
    F_full, B_full, _ = \
        build_trajectories_v10(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # FIX A + FIX C: modified source builder
    tract_src, bypass_segs = \
        build_source_and_bypass(specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos+len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

    # Nasal antiformants
    T = 1.0/sr
    NASAL_AF = {
        'M':  (1000, 300),
        'N':  (1500, 350),
        'NG': (2000, 400),
    }
    pos = 0
    for spec in specs:
        ph  = spec['ph']
        n_s = spec['n_s']
        if ph in NASAL_AF:
            af, abw = NASAL_AF[ph]
            seg     = out[pos:pos+n_s].copy()
            anti    = np.zeros(n_s, dtype=DTYPE)
            y1 = y2 = 0.0
            for i in range(n_s):
                a2 = -np.exp(-2*np.pi*abw*T)
                a1 =  2*np.exp(-np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0 = 1.0-a1-a2
                y  = b0*float(seg[i]) + \
                     a1*y1 + a2*y2
                y2 = y1; y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:pos+n_s] = 0.0
        pos += n_s

    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    atk = int(0.025*sr)
    rel = int(0.055*sr)
    env = f32(np.ones(n_total))
    if atk > 0 and atk < n_total:
        env[:atk] = f32(np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(np.linspace(1, 0, rel))
    out = out * f32(amp_env) * env

    segs_out = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s     = spec['n_s']
        segs_out.append(out[pos:pos+n_s].copy())
        rest_ms = item.get('rest_ms', 0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(rest_ms, sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))
    p95   = np.percentile(np.abs(final), 95)
    if p95 > 1e-8:
        final = final / p95 * 0.88
    final = np.clip(final, -1.0, 1.0)
    return final


def synth_word(word, punct='.',
               pitch=PITCH, dil=DIL,
               sr=SR):
    syls = WORD_SYLLABLES.get(word.lower())
    if syls is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))
    flat = [p for s in syls for p in s]
    return synth_phrase(
        [(word, flat)],
        punctuation=punct,
        pitch_base=pitch,
        dil=dil, sr=sr)


def save(name, sig, room=True,
          rt60=1.5, dr=0.50, sr=SR):
    sig = f32(sig)
    if room:
        sig = apply_room(
            sig, rt60=rt60, dr=dr, sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v10")
    print("Onset fixes — driven by onset_diagnostic.")
    print()
    print("  FIX A: DH voiced fade-in")
    print("         First 25ms: bypass only.")
    print("         Voiced rises 0→0.30 after.")
    print("         Dental friction IS the onset.")
    print("         No 'ea' prefix.")
    print()
    print("  FIX B: H neutral onset formants")
    print("         First 30ms: pharyngeal shape.")
    print("         Blends toward next vowel.")
    print("         No palatal peak at t=0.")
    print("         No 'CH' prefix.")
    print()
    print("  FIX C: Full transition bypass delay")
    print("         Bypass starts after full n_on.")
    print("         No vowel/sibilant overlap.")
    print("         No dragged S or Z.")
    print("="*60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    # Step 1: Run onset diagnostic first.
    # This tells us immediately whether
    # the fixes are working before we
    # have to listen.
    print("  Running onset diagnostic...")
    print()
    from onset_diagnostic import \
        run_onset_diagnostic
    results, n_pass, n_fail = \
        run_onset_diagnostic(
            synth_phrase, PITCH, sr=SR)
    print()

    # Step 2: Primary phrase
    print("  Primary phrase...")
    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L',  'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]
    seg = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    # Step 3: Targeted isolation tests
    print()
    print("  Isolation tests...")
    for label, words, note in [
        ('test_the',
         [('the', ['DH', 'AH'])],
         'no ea-prefix'),
        ('test_here',
         [('here', ['H', 'IH', 'R'])],
         'breathy, no CH-prefix'),
        ('test_was',
         [('was', ['W', 'AH', 'Z'])],
         'Z ends at vowel boundary'),
        ('test_voice',
         [('voice', ['V', 'OY', 'S'])],
         'S follows OY naturally'),
        ('test_this_is_here',
         [('this', ['DH', 'IH', 'S']),
          ('is',   ['IH', 'Z']),
          ('here', ['H',  'IH', 'R'])],
         'multiple DH and H in phrase'),
    ]:
        seg = synth_phrase(
            words, pitch_base=PITCH)
        write_wav(
            f"output_play/{label}.wav",
            apply_room(seg, rt60=1.2,
                        dr=0.55))
        print(f"    {label}.wav  ({note})")

    # Step 4: Sentence types
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            PHRASE, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/the_voice_{label}.wav",
            apply_room(seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Step 5: Additional coverage
    print()
    print("  Additional phrases...")
    for label, words, punct in [
        ('water_home',
         [('water', ['W','AA','T','ER']),
          ('home',  ['H','OW','M'])], '.'),
        ('still_here',
         [('still', ['S','T','IH','L']),
          ('here',  ['H','IH','R'])], '.'),
        ('here_and_there',
         [('here',  ['H', 'IH', 'R']),
          ('and',   ['AE','N',  'D']),
          ('there', ['DH','EH', 'R'])], '.'),
        ('not_yet',
         [('not', ['N','AA','T']),
          ('yet', ['Y','EH','T'])], '.'),
    ]:
        seg = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/phrase_{label}.wav",
            apply_room(seg, rt60=1.6, dr=0.48))
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  ONSET DIAGNOSTIC:")
    print(f"  {n_pass} passing / "
          f"{n_pass+n_fail} total")
    if n_fail == 0:
        print("  ALL PASSING — onset artifacts gone.")
    else:
        print("  Failing checks printed above.")
        print("  Adjust constants and re-run.")
    print()
    print("  LISTEN:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  FOUR TESTS:")
    print("  afplay output_play/test_the.wav")
    print("  afplay output_play/test_here.wav")
    print("  afplay output_play/test_was.wav")
    print("  afplay output_play/test_voice.wav")
    print()
    print("  If onset diagnostic passes")
    print("  but you still hear the artifacts,")
    print("  the targets in ONSET_TARGETS")
    print("  need to be tightened.")
    print("  Tighten the target that")
    print("  corresponds to what you hear,")
    print("  re-run, and the diagnostic")
    print("  will guide the next fix.")
    print()
