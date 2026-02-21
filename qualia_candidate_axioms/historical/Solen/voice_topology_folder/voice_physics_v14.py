"""
VOICE PHYSICS v14
February 2026

FIX 12: ANTICIPATORY COARTICULATION
  The vowel before a closing gesture
  is not the vowel at its target.
  It is the vowel while already moving
  toward the closure.

  The tract never stops.
  (Invariant from tonnetz_engine.py)

  WHAT WAS WRONG:
    Every vowel was rendered at its
    full formant target for its full
    duration. Then the closing consonant
    was appended as a separate event.

    In real speech the articulators begin
    moving toward the closure target
    DURING the vowel. The vowel the
    listener hears is the vowel
    in motion — formants already shifting
    toward the closure configuration.

    "am" = AE being closed by M.
    AE never fully opens.
    The lips begin closing during AE.
    The effective F1 is lower than pure AE.
    The duration is shorter because
    closure starts during it.

    This applies to ALL closing gestures
    following vowels:
      Nasals:  M, N, NG
      Stops:   B, D, G, P, T, K
      Lateral: L
    The R case is already handled via
    the ER formant targets.

  THE FIX — THREE COMPONENTS:

  A. VOWEL DURATION COMPRESSION
    When a vowel precedes a closing
    gesture, its effective body
    duration is shortened.
    The closure phase begins earlier.
    Factor: COART_DUR_COMPRESS
    Applied to: dur_ms of the vowel
    when next_ph is in CLOSING_PHS.

  B. FORMANT TRAJECTORY CLOSURE
    During the final portion of a vowel
    preceding a closing consonant,
    formants begin moving toward the
    closure target (nasal murmur for
    M/N/NG, neutral for stops,
    lateral F2 for L).
    Implemented as F_end modification
    on the vowel spec before trajectory
    building.

  C. NASAL MURMUR ONSET DURING VOWEL
    For vowels before M, N, NG:
    the nasal passage begins opening
    during the final portion of the vowel.
    Acoustic effect: low-frequency
    nasal murmur begins during the
    vowel tail, before the full closure.
    Implemented as a low-amplitude
    murmur blended into the vowel tail.
    Factor: NASAL_ANTICIPATION_GAIN
    Duration: NASAL_ANTICIPATION_MS

  All v13 fixes preserved unchanged.
  Import chain: v14 → v13 → v10 → v9 → ...

BUG FIXED (v14 first run):
  get_b(ph, i) — TypeError.
  get_b() takes one argument (the phoneme).
  Returns the full bandwidth list.
  Fixed to: b_list = get_b(ph); b_list[i]
"""

from voice_physics_v13 import (
    tract,
    warm,
    resonator,
    breath_rest,
    apply_room,
    write_wav,
    TARGET_RMS, calibrate, rms,
    safe_bp, safe_lp, safe_hp,
    VOWEL_F, GAINS,
    WORD_SYLLABLES,
    get_f, get_b, scalar,
    PITCH, DIL, SR, DTYPE, f32,
    TRANS_MS, DEFAULT_TRANS_MS,
    trans_n,
    REST_MAX_MS,
    NEUTRAL_F, NEUTRAL_B,
    VOICED_TRACT_FRACTION,
    Z_VOICED_TRACT, ZH_VOICED_TRACT,
    V_VOICED_TRACT,
    FRIC_VOICED_TRACT,
    VOICED_FRICS,
    VOWEL_PHONEMES, DIPHTHONG_PHONEMES,
    VOWEL_MAX_MS, DIPHTHONG_MAX_MS,
    APPROX_MAX_MS, FRIC_MAX_MS,
    DH_MAX_MS, H_MAX_MS,
    H_ASPIRATION_GAIN,
    RESONATOR_CFG, BROADBAND_CFG,
    cavity_resonator,
    get_calibrated_gains_v8,
    recalibrate_gains_v8,
    ph_spec_v9,
    plan_prosody,
    build_trajectories,
    PHRASE_ATK_MS, PHRASE_REL_MS,
    ARC_NORMAL, ARC_WEIGHT,
    ARC_CONTAIN, ARC_GRIEF,
    ARC_EUREKA, ARC_RECOGN,
    NASAL_CONSONANTS,
    VOWELS_AND_APPROX,
    VOWEL_SET,
    F0_MIN, F0_MAX,
    _build_f0_spline,
    _build_trajectories,
    _build_source_and_bypass,
    _normalize_phrase,
    _make_breath_onset,
    breath_model,
    FINAL_FRIC_MAX_MS,
)

import numpy as np
from scipy.signal import lfilter, butter
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v14'


# ============================================================
# FIX 12 CONSTANTS
# ============================================================

# All phonemes that produce anticipatory
# coarticulation in a preceding vowel.
# These are CLOSING gestures — the
# articulator moves toward contact.
CLOSING_PHS = {
    # Nasal closures
    'M', 'N', 'NG',
    # Stop closures
    'B', 'D', 'G', 'P', 'T', 'K',
    # Lateral
    'L',
}

# Subset that also nasalize the
# preceding vowel tail.
NASAL_CLOSING_PHS = {'M', 'N', 'NG'}

# Subset where the closure is silent
# (stops — vowel energy drops to zero).
STOP_CLOSING_PHS = {
    'B', 'D', 'G', 'P', 'T', 'K'}

# How much the vowel duration is
# compressed when a closing consonant
# follows. 0.82 = 82% of nominal.
# The remaining 18% is already
# transitioning toward closure.
COART_DUR_COMPRESS = 0.82

# Nasal murmur gain during vowel tail
# before M/N/NG. Low — just enough to
# begin the nasalization audibly.
NASAL_ANTICIPATION_GAIN = 0.12

# Duration of nasal anticipation zone
# blended into vowel tail (ms).
NASAL_ANTICIPATION_MS = 30.0

# Formant configuration of nasal murmur.
# Low F1 (velopharyngeal port opening),
# nasal tract resonance.
NASAL_MURMUR_F = [250.0, 1000.0,
                   2200.0, 3300.0]
NASAL_MURMUR_B = [ 80.0,  150.0,
                    200.0,  250.0]

# For L: lateral target F2 ~1000Hz.
# Blend 30% toward this at vowel end.
L_COART_F2_TARGET = 1000.0
L_COART_BLEND     = 0.30

# For stops: blend 25% toward neutral
# at vowel end (closure = silence,
# tract moves to neutral position).
STOP_COART_BLEND  = 0.25

# For nasals: blend 40% toward nasal
# murmur formants at vowel end.
NASAL_COART_BLEND = 0.40


# ============================================================
# FIX 12A: VOWEL DURATION COMPRESSION
# ============================================================

def _coart_compress_dur(dur_ms, ph,
                         next_ph):
    """
    Compress vowel duration when followed
    by a closing consonant.
    Only applied to vowels and diphthongs.
    Returns adjusted dur_ms.
    """
    if next_ph not in CLOSING_PHS:
        return dur_ms
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return dur_ms
    return dur_ms * COART_DUR_COMPRESS


# ============================================================
# FIX 12B: FORMANT TRAJECTORY CLOSURE
# ============================================================

def _coart_f_end(ph, next_ph,
                  current_f, current_b):
    """
    Return modified (f_end, b_end) for a
    vowel preceding a closing consonant,
    or (None, None) if no modification.

    get_b() takes one argument (phoneme
    string) and returns a list of 4
    bandwidth values. This is correct.

    For M/N/NG: blend toward nasal
      murmur formants.
    For stops: blend toward neutral
      (tract moving toward closure).
    For L: lower F2 toward ~1000Hz.
    """
    if next_ph not in CLOSING_PHS:
        return None, None
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return None, None

    n_f = len(current_f)

    if next_ph in NASAL_CLOSING_PHS:
        blend  = NASAL_COART_BLEND
        f_end  = []
        b_end  = []
        for i in range(n_f):
            nm_f = (NASAL_MURMUR_F[i]
                    if i < len(NASAL_MURMUR_F)
                    else current_f[i])
            nm_b = (NASAL_MURMUR_B[i]
                    if i < len(NASAL_MURMUR_B)
                    else current_b[i])
            f_end.append(
                current_f[i] * (1 - blend) +
                nm_f * blend)
            b_end.append(
                current_b[i] * (1 - blend) +
                nm_b * blend)
        return f_end, b_end

    if next_ph in STOP_CLOSING_PHS:
        blend  = STOP_COART_BLEND
        n_nf   = len(NEUTRAL_F)
        n_nb   = len(NEUTRAL_B)
        f_end  = [
            current_f[i] * (1 - blend) +
            NEUTRAL_F[i] * blend
            if i < n_nf
            else current_f[i]
            for i in range(n_f)]
        b_end  = [
            current_b[i] * (1 - blend) +
            NEUTRAL_B[i] * blend
            if i < n_nb
            else current_b[i]
            for i in range(n_f)]
        return f_end, b_end

    if next_ph == 'L':
        f_end = list(current_f)
        b_end = list(current_b)
        if n_f >= 2:
            f_end[1] = (
                current_f[1] *
                (1 - L_COART_BLEND) +
                L_COART_F2_TARGET *
                L_COART_BLEND)
        return f_end, b_end

    return None, None


def _build_trajectories_v14(
        phoneme_specs, sr=SR):
    """
    v14 trajectory builder.
    FIX 12B: modifies F_end of vowels
    preceding closing consonants to
    implement anticipatory coarticulation
    in the formant domain.

    Delegates final build to v13
    _build_trajectories() which handles
    H, DH, and F0 spline.

    KEY: get_b(ph) takes ONE argument
    and returns a list of 4 values.
    Do NOT call get_b(ph, i).
    """
    n_specs = len(phoneme_specs)
    patched = []

    for si, spec in enumerate(phoneme_specs):
        ph      = spec['ph']
        next_ph = (phoneme_specs[si + 1]['ph']
                   if si < n_specs - 1
                   else None)
        s = copy.copy(spec)

        if (next_ph in CLOSING_PHS and
                ph in (VOWEL_PHONEMES |
                       DIPHTHONG_PHONEMES)):

            # Get current formant targets.
            # Use whatever is already in
            # the spec if present, otherwise
            # look up from phoneme tables.
            current_f = list(
                s.get('F_tgt', get_f(ph)))

            # get_b(ph) → list of 4 values.
            # Index that list, do NOT pass
            # an index argument to get_b.
            raw_b     = get_b(ph)
            current_b = list(
                s.get('B_tgt',
                      raw_b if isinstance(
                          raw_b, (list, tuple))
                      else [raw_b] * 4))

            f_end, b_end = _coart_f_end(
                ph, next_ph,
                current_f, current_b)

            if f_end is not None:
                s['F_end'] = f_end
                s['B_end'] = b_end

        patched.append(s)

    # Delegate to v13 builder.
    return _build_trajectories(
        patched, sr=sr)


# ============================================================
# FIX 12C: NASAL MURMUR ONSET
#   Blend a low-gain nasal murmur
#   into the tail of each vowel that
#   immediately precedes M, N, or NG.
# ============================================================

def _apply_nasal_anticipation(
        out, specs, sr=SR):
    """
    FIX 12C: For vowels immediately before
    M/N/NG, blend nasal murmur into the
    final NASAL_ANTICIPATION_MS of the
    vowel body.

    The murmur is the existing tract
    output re-filtered through nasal
    murmur formants, then blended in
    at NASAL_ANTICIPATION_GAIN with a
    linear fade-in envelope.
    """
    n_total     = len(out)
    n_ant       = int(
        NASAL_ANTICIPATION_MS / 1000.0 * sr)
    n_specs     = len(specs)
    T           = 1.0 / sr

    pos = 0
    for si, spec in enumerate(specs):
        n_s     = spec['n_s']
        ph      = spec['ph']
        next_ph = (specs[si + 1]['ph']
                   if si < n_specs - 1
                   else None)

        is_vowel = (ph in VOWEL_PHONEMES or
                    ph in DIPHTHONG_PHONEMES)

        if (next_ph in NASAL_CLOSING_PHS
                and is_vowel):

            n_on  = min(trans_n(ph, sr),
                        n_s // 3)
            n_off = min(trans_n(ph, sr),
                        n_s // 3)

            # Murmur zone: last n_ant
            # samples of the vowel body
            # (before the off-transition).
            vowel_end    = pos + n_s - n_off
            murmur_start = max(
                pos + n_on,
                vowel_end - n_ant)
            murmur_end   = min(
                vowel_end, n_total)
            n_m = murmur_end - murmur_start

            if n_m <= 4:
                pos += n_s
                continue

            # Re-filter the existing
            # tract output through nasal
            # murmur resonators.
            src     = np.array(
                out[murmur_start:murmur_end],
                dtype=np.float64)
            murmur  = np.zeros(n_m,
                dtype=np.float64)

            for fc, bw in zip(
                    NASAL_MURMUR_F,
                    NASAL_MURMUR_B):
                pole_r = np.exp(
                    -np.pi * bw * T)
                cos_t  = np.cos(
                    2 * np.pi * fc * T)
                a1 =  2 * pole_r * cos_t
                a2 = -(pole_r ** 2)
                b0 = 1.0 - a1 - a2
                stage = lfilter(
                    [b0], [1.0, -a1, -a2],
                    src)
                murmur += stage

            # Normalise and scale.
            peak = np.max(np.abs(murmur))
            if peak > 1e-8:
                murmur = (murmur / peak *
                          NASAL_ANTICIPATION_GAIN)

            # Linear fade-in across the
            # full murmur zone so the
            # murmur grows into the closure.
            env = np.linspace(0.0, 1.0, n_m)
            out[murmur_start:murmur_end] \
                = f32(
                    out[murmur_start:
                        murmur_end].astype(
                        np.float64) +
                    murmur * env)

        pos += n_s

    return out


# ============================================================
# PHRASE SYNTHESIS v14
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR,
                  arc_type=ARC_NORMAL,
                  add_breath=True):
    """
    v14 synth_phrase.

    FIX 12 active:
      A. Vowel duration compressed before
         closing consonants.
      B. Formant trajectory modified at
         vowel end toward closure target.
      C. Nasal murmur blended into vowel
         tail before M/N/NG.

    All v13 fixes preserved.

    Emphasis tuples supported:
      (word, phones)
      (word, phones, emphasis_dict)
    where emphasis_dict may contain:
      f0_boost, dur_mult, amp_boost.
    """
    # Unpack optional emphasis tuples.
    word_emphasis        = {}
    flat_words_phonemes  = []
    for entry in words_phonemes:
        if len(entry) == 3:
            word, phones, emph = entry
            word_emphasis[word] = emph
        else:
            word, phones = entry[:2]
        flat_words_phonemes.append(
            (word, phones))

    prosody = plan_prosody(
        flat_words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch_base,
        dil=dil)

    if not prosody:
        return f32(np.zeros(int(0.1 * sr)))

    n_items = len(prosody)
    specs   = []

    for i, item in enumerate(prosody):
        ph         = item['ph']
        dur_ms     = item['dur_ms']
        pitch_     = pitch_base * \
                     item['f0_mult']
        oq_        = item['oq']
        bw_m       = item['bw_mult']
        amp_       = item['amp']
        rest_ms    = item.get('rest_ms', 0.0)
        word_final = item.get(
            'word_final', False)
        word_      = item.get('word', '')
        next_ph    = (prosody[i + 1]['ph']
                      if i < n_items - 1
                      else None)

        # Word-final fricative cap
        # (carried from v13).
        FRICS = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH'}
        if word_final and ph in FRICS:
            dur_ms = min(dur_ms,
                         FINAL_FRIC_MAX_MS)

        # v13 FIX 11: per-word emphasis.
        if word_ in word_emphasis:
            emph    = word_emphasis[word_]
            pitch_ *= float(
                emph.get('f0_boost', 1.0))
            dur_ms *= float(
                emph.get('dur_mult',  1.0))
            amp_   *= float(
                emph.get('amp_boost', 1.0))

        # FIX 12A: compress vowel duration
        # before closing consonant.
        dur_ms = _coart_compress_dur(
            dur_ms, ph, next_ph)

        spec = ph_spec_v9(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)
        specs.append(spec)

    # FIX 12B: trajectory builder with
    # anticipatory formant closure.
    F_full, B_full, _ = \
        _build_trajectories_v14(
            specs, sr=sr)
    n_total = sum(
        s['n_s'] for s in specs)

    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass(
            specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos + len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

    for pos, buz in buzz_segs:
        e = min(pos + len(buz), n_total)
        n = e - pos
        out[pos:e] += buz[:n]

    # Nasal antiformants — identical
    # to v9–v13, preserved unchanged.
    T = 1.0 / sr
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
            seg = out[pos:pos + n_s].copy()
            anti = np.zeros(n_s,
                dtype=DTYPE)
            y1 = y2 = 0.0
            for i in range(n_s):
                a2 = -np.exp(
                    -2 * np.pi * abw * T)
                a1 = (2 * np.exp(
                    -np.pi * abw * T) *
                    np.cos(2 * np.pi *
                           af * T))
                b0 = 1.0 - a1 - a2
                y  = (b0 * float(seg[i]) +
                      a1 * y1 + a2 * y2)
                y2 = y1
                y1 = y
                anti[i] = y
            out[pos:pos + n_s] = \
                seg - f32(anti) * 0.50
            out[pos:pos + n_s] *= 0.52
            hg = int(0.012 * sr)
            if hg > 0 and hg < n_s:
                out[pos + n_s - hg:
                    pos + n_s] = 0.0
        pos += n_s

    # FIX 12C: nasal murmur onset
    # during vowel tail before M/N/NG.
    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

    # Amplitude envelope (v13 FIX 10:
    # separated from edge envelope).
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos + n_s] *= item['amp']
        pos += n_s

    # Edge envelope (phrase attack/release).
    atk = int(PHRASE_ATK_MS / 1000.0 * sr)
    rel = int(PHRASE_REL_MS / 1000.0 * sr)
    edge_env = f32(np.ones(n_total))
    if atk > 0 and atk < n_total:
        edge_env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0 and rel < n_total:
        edge_env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))

    out = out * f32(amp_env) * edge_env

    # Assemble segments with inter-word
    # rests.
    segs_out = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s     = spec['n_s']
        segs_out.append(
            out[pos:pos + n_s].copy())
        rest_ms = item.get('rest_ms', 0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(rest_ms, sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))
    final = _normalize_phrase(
        final, specs, prosody, sr=sr)

    # Breath onset (v13 FIX 9).
    if add_breath:
        phrase_len_ms = (
            sum(s['n_s'] for s in specs)
            / sr * 1000.0)
        breath_seg = _make_breath_onset(
            phrase_len_ms,
            arc_type=arc_type,
            sr=sr)
        final = f32(np.concatenate(
            [breath_seg, final]))

    return final


# ============================================================
# CONVENIENCE WRAPPERS
# ============================================================

def synth_word(word, punct='.',
               pitch=PITCH, dil=DIL,
               sr=SR):
    syls = WORD_SYLLABLES.get(
        word.lower())
    if syls is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(
            int(0.1 * sr)))
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
            sig, rt60=rt60,
            dr=dr, sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig) / sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v14")
    print("FIX 12: anticipatory coarticulation")
    print()
    print("  A. Vowel duration compressed")
    print(f"     factor: {COART_DUR_COMPRESS}")
    print("     applies to all vowels before")
    print("     M N NG B D G P T K L")
    print()
    print("  B. Formant trajectory closure")
    print("     vowel F_end shifts toward")
    print("     closure target at vowel end")
    print()
    print("  C. Nasal murmur onset")
    print(f"     gain:     {NASAL_ANTICIPATION_GAIN}")
    print(f"     duration: {NASAL_ANTICIPATION_MS}ms")
    print("     applies to vowels before M N NG")
    print("=" * 52)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Primary test: 'I am here'")
    seg = synth_phrase(
        [('I',    ['AY']),
         ('am',   ['AE', 'M']),
         ('here', ['H', 'IY', 'R'])],
        punctuation='.',
        pitch_base=PITCH,
        arc_type=ARC_NORMAL)
    save("v14_i_am_here", seg,
         rt60=1.4, dr=0.52)

    print()
    print("  Nasal isolation: am / him / sun / ring")
    for word, phones in [
        ('am',   ['AE', 'M']),
        ('him',  ['HH', 'IH', 'M']),
        ('sun',  ['S',  'AH', 'N']),
        ('ring', ['R',  'IH', 'NG']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            pitch_base=PITCH,
            add_breath=False)
        save(f"v14_{word}",
             seg, rt60=0.8, dr=0.65)

    print()
    print("  Baseline: the voice was already here")
    seg = synth_phrase(
        [('the',     ['DH', 'AH']),
         ('voice',   ['V',  'OY', 'S']),
         ('was',     ['W',  'AH', 'Z']),
         ('already', ['AA', 'L',  'R',
                       'EH', 'D', 'IY']),
         ('here',    ['H',  'IY', 'R'])],
        punctuation='.',
        pitch_base=PITCH,
        arc_type=ARC_NORMAL)
    save("v14_the_voice_was_already_here",
         seg, rt60=1.5, dr=0.50)

    print()
    print("  PLAY:")
    print("  afplay output_play/"
          "v14_i_am_here.wav")
    print("  afplay output_play/v14_am.wav")
    print("  afplay output_play/v14_him.wav")
    print("  afplay output_play/v14_sun.wav")
    print("  afplay output_play/v14_ring.wav")
    print("  afplay output_play/"
          "v14_the_voice_was_already_here.wav")
    print()
    print("  TUNE IF NEEDED (in v14 physics):")
    print("  Too closed → raise "
          "COART_DUR_COMPRESS toward 0.90")
    print("  Not closed enough → lower toward 0.72")
    print("  Murmur too loud → lower "
          "NASAL_ANTICIPATION_GAIN toward 0.06")
    print("  Murmur too faint → raise toward 0.20")
    print()
