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
    Applied to: n_body of the vowel
    when next_ph is in CLOSING_PHS.

  B. FORMANT TRAJECTORY CLOSURE
    During the final COART_TAIL_MS
    of a vowel preceding a closing
    consonant, formants begin moving
    toward the closure target
    (nasal murmur for M/N/NG,
     silence for stops,
     lateral configuration for L).
    This happens inside build_trajectories
    via F_end modification when
    next_ph is a closing consonant.

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
  Import chain: v14 → v13 → v9 → v8 ...
"""

from voice_physics_v13 import (
    # all v13 exports
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
    # v13 specifics
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

# Phonemes that produce anticipatory
# coarticulation in a preceding vowel.
# These are all CLOSING gestures —
# the articulator moves toward a
# more closed/contact configuration.
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
# (stops — vowel energy simply drops).
STOP_CLOSING_PHS = {
    'B', 'D', 'G', 'P', 'T', 'K'}

# How far back into the vowel the
# anticipatory coarticulation begins,
# in ms from vowel end.
COART_TAIL_MS = 45.0

# How much the vowel body is compressed
# when a closing consonant follows.
# 0.80 = vowel body is 80% of nominal.
# The remaining 20% is the anticipatory
# transition zone.
COART_DUR_COMPRESS = 0.82

# Nasal murmur gain during vowel tail
# before M/N/NG. Low — just enough
# to begin the nasalization.
NASAL_ANTICIPATION_GAIN = 0.12

# Duration of nasal anticipation
# blended into vowel tail (ms).
NASAL_ANTICIPATION_MS = 30.0

# Formant targets for nasal murmur
# (low F1 configuration, open velum).
# Used to color the vowel tail before
# nasal closure.
NASAL_MURMUR_F = [250.0, 1000.0,
                   2200.0, 3300.0,
                   4000.0]
NASAL_MURMUR_B = [ 80.0,  150.0,
                    200.0,  250.0,
                    300.0]

# For L: the lateral adds a lowered
# F2 trajectory toward ~1000Hz.
# This is applied as a formant
# end-point modification.
L_COART_F2_TARGET = 1000.0


# ============================================================
# FIX 12A: VOWEL DURATION COMPRESSION
#
# Called from synth_phrase() during
# spec construction.
# If the vowel is followed by a
# closing consonant, compress its
# body duration slightly.
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
#
# Modifies F_end of vowel specs so
# that the tract is already moving
# toward the closure target at vowel
# end.
# Applied inside _build_trajectories_v14.
# ============================================================

def _coart_f_end(ph, next_ph,
                  current_f, current_b):
    """
    Return modified F_end target for a
    vowel preceding a closing consonant.

    For M/N/NG: blend toward nasal
      murmur formants.
    For stops: blend toward neutral
      (closure = silence, no formant
      identity).
    For L: lower F2 toward lateral
      target.

    Returns (f_end, b_end) as lists,
    or None if no modification needed.
    """
    if next_ph not in CLOSING_PHS:
        return None, None
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return None, None

    n_f = len(current_f)

    if next_ph in NASAL_CLOSING_PHS:
        # Blend 40% toward nasal murmur
        blend = 0.40
        f_end = []
        b_end = []
        for i in range(n_f):
            nm_f = (NASAL_MURMUR_F[i]
                    if i < len(NASAL_MURMUR_F)
                    else current_f[i])
            nm_b = (NASAL_MURMUR_B[i]
                    if i < len(NASAL_MURMUR_B)
                    else current_b[i])
            f_end.append(
                current_f[i] * (1-blend) +
                nm_f * blend)
            b_end.append(
                current_b[i] * (1-blend) +
                nm_b * blend)
        return f_end, b_end

    if next_ph in STOP_CLOSING_PHS:
        # Blend 25% toward neutral
        # (tract moving toward closure)
        blend = 0.25
        f_end = [
            current_f[i] * (1-blend) +
            NEUTRAL_F[i] * blend
            if i < len(NEUTRAL_F)
            else current_f[i]
            for i in range(n_f)]
        b_end = [
            current_b[i] * (1-blend) +
            NEUTRAL_B[i] * blend
            if i < len(NEUTRAL_B)
            else current_b[i]
            for i in range(n_f)]
        return f_end, b_end

    if next_ph == 'L':
        # Lower F2 toward lateral target
        f_end = list(current_f)
        b_end = list(current_b)
        if n_f >= 2:
            f_end[1] = (
                current_f[1] * 0.70 +
                L_COART_F2_TARGET * 0.30)
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
    """
    n_specs = len(phoneme_specs)
    patched = []
    for si, spec in enumerate(
            phoneme_specs):
        ph      = spec['ph']
        next_ph = (phoneme_specs[si+1]['ph']
                   if si < n_specs-1
                   else None)
        s = copy.copy(spec)

        # FIX 12B: vowel formant closure
        if next_ph in CLOSING_PHS and \
           ph in (VOWEL_PHONEMES |
                  DIPHTHONG_PHONEMES):
            current_f = list(
                s.get('F_tgt',
                      get_f(ph)))
            current_b = list(
                s.get('B_tgt',
                      [get_b(ph, i)
                       for i in range(
                           len(current_f))]))
            f_end, b_end = _coart_f_end(
                ph, next_ph,
                current_f, current_b)
            if f_end is not None:
                s['F_end'] = f_end
                s['B_end'] = b_end

        patched.append(s)

    # Delegate to v13 trajectory builder
    # which handles H, DH, and spline.
    return _build_trajectories(
        patched, sr=sr)


# ============================================================
# FIX 12C: NASAL MURMUR ONSET
#
# After the tract output is assembled,
# blend a low-gain nasal murmur into
# the tail of each vowel that precedes
# M, N, or NG.
# ============================================================

def _apply_nasal_anticipation(
        out, specs, sr=SR):
    """
    FIX 12C: For vowels immediately
    before M/N/NG, blend nasal murmur
    into the final NASAL_ANTICIPATION_MS
    of the vowel.

    The murmur is synthesized as
    voiced source through nasal
    formant configuration.
    Gain: NASAL_ANTICIPATION_GAIN.
    Onset: last NASAL_ANTICIPATION_MS
    of the vowel body.
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
        next_ph = (specs[si+1]['ph']
                   if si < n_specs-1
                   else None)

        if next_ph in NASAL_CLOSING_PHS \
           and ph in (VOWEL_PHONEMES |
                      DIPHTHONG_PHONEMES):
            # Compute murmur zone
            n_on  = min(trans_n(ph, sr),
                        n_s // 3)
            n_off = min(trans_n(ph, sr),
                        n_s // 3)
            n_body = max(0,
                         n_s - n_on - n_off)
            # Murmur starts n_ant before
            # end of vowel body
            murmur_start = max(
                pos + n_on,
                pos + n_s - n_off - n_ant)
            murmur_end   = min(
                pos + n_s - n_off,
                n_total)
            n_m = murmur_end - murmur_start
            if n_m <= 0:
                pos += n_s
                continue

            # Generate nasal murmur
            # via IIR resonators
            murmur = np.zeros(n_m,
                dtype=np.float64)
            # Use voiced source from
            # surrounding region
            src = out[murmur_start:
                      murmur_end].copy()
            src = np.array(src,
                dtype=np.float64)
            # Apply nasal formants
            for fc, bw in zip(
                    NASAL_MURMUR_F[:3],
                    NASAL_MURMUR_B[:3]):
                pole_r = np.exp(
                    -np.pi * bw * T)
                cos_t  = np.cos(
                    2*np.pi*fc*T)
                a1 =  2*pole_r*cos_t
                a2 = -(pole_r**2)
                b0 = 1 - a1 - a2
                stage = lfilter(
                    [b0], [1, -a1, -a2],
                    src)
                murmur += stage

            murmur = f32(murmur)
            if np.max(np.abs(murmur)) > 1e-8:
                murmur = (murmur /
                    np.max(np.abs(murmur))
                    * NASAL_ANTICIPATION_GAIN)

            # Fade in murmur over full zone
            env = f32(np.linspace(
                0.0, 1.0, n_m))
            out[murmur_start:murmur_end] \
                += f32(murmur * env)

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
    v14: FIX 12 active.
      A. Vowel duration compressed before
         closing consonants.
      B. Formant trajectories modified
         at vowel end toward closure target.
      C. Nasal murmur blended into vowel
         tail before M/N/NG.
    All v13 fixes preserved.
    """
    # Parse emphasis (v13 FIX 11)
    word_emphasis = {}
    flat_words_phonemes = []
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
        return f32(np.zeros(int(0.1*sr)))

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
        rest_ms    = item.get(
            'rest_ms', 0.0)
        word_final = item.get(
            'word_final', False)
        next_ph    = (prosody[i+1]['ph']
                      if i < n_items-1
                      else None)
        word_      = item.get('word', '')

        FRICS = {'S','Z','SH','ZH',
                 'F','V','TH','DH'}
        if word_final and ph in FRICS:
            dur_ms = min(
                dur_ms, FINAL_FRIC_MAX_MS)

        # v13 FIX 11: per-word emphasis
        if word_ in word_emphasis:
            emph = word_emphasis[word_]
            pitch_ *= float(
                emph.get('f0_boost', 1.0))
            dur_ms *= float(
                emph.get('dur_mult',  1.0))
            amp_   *= float(
                emph.get('amp_boost', 1.0))

        # FIX 12A: compress vowel before
        # closing consonant
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
    # formant closure modification
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
        e = min(pos+len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

    for pos, buz in buzz_segs:
        e = min(pos+len(buz), n_total)
        n = e - pos
        out[pos:e] += buz[:n]

    # Nasal antiformants (v9, preserved)
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
            seg     = out[pos:pos+n_s].copy()
            anti    = np.zeros(n_s,
                dtype=DTYPE)
            y1 = y2 = 0.0
            for i in range(n_s):
                a2 = -np.exp(
                    -2*np.pi*abw*T)
                a1 = (2*np.exp(
                    -np.pi*abw*T) *
                    np.cos(2*np.pi*af*T))
                b0 = 1.0 - a1 - a2
                y  = (b0*float(seg[i]) +
                      a1*y1 + a2*y2)
                y2 = y1; y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:
                    pos+n_s] = 0.0
        pos += n_s

    # FIX 12C: nasal anticipation murmur
    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

    # v13 FIX 10: separated envelopes
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

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

    segs_out = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s     = spec['n_s']
        segs_out.append(
            out[pos:pos+n_s].copy())
        rest_ms = item.get('rest_ms', 0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(rest_ms, sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))
    final = _normalize_phrase(
        final, specs, prosody, sr=sr)

    if add_breath:
        phrase_len_ms = sum(
            s['n_s'] for s in specs
        ) / sr * 1000.0
        breath_seg = _make_breath_onset(
            phrase_len_ms,
            arc_type=arc_type, sr=sr)
        final = f32(np.concatenate(
            [breath_seg, final]))

    return final
