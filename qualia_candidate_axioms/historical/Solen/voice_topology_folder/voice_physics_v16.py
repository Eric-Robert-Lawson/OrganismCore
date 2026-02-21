"""
VOICE PHYSICS v16
February 2026

FIX 14: THE H GHOST LAYER

  H Ghost Topology (h_ghost_topology.md v2)
  established that:

    H is the Tonnetz origin.
    The baseline state of the voice.
    Every syllable cycle is:
      H → onset → nucleus → coda → H

    The inter-syllable ghost is the
    acoustic trace of the tract
    returning to H between beats.

    The ghost is not decoration.
    It is the qualia carrier.
    The words carry meaning.
    The ghost carries the experience
    of meaning.

  WHAT IS NEW IN v16:

  1. SYLLABIFIED INPUT FORMAT
     synth_phrase() now accepts nested
     phoneme lists encoding syllable
     boundaries:

       ('already', [['AO','L'],
                    ['R','EH'],
                    ['D','IY']])

     Flat list still accepted for
     backward compatibility:

       ('already', ['AO','L','R',
                    'EH','D','IY'])

     With syllable boundaries, the engine
     knows where every ghost belongs.
     Without them, it places one ghost
     per word boundary only (v15 behavior).

  2. INTER-SYLLABLE GHOST
     At every syllable boundary, a brief
     H-filtered micro-segment is inserted.
     Duration and amplitude computed by
     ghost_at_boundary() from tonnetz_engine,
     which uses:
       - Tonnetz distance between adjacent
         nucleus vowels
       - Arc type (ghost signature)
       - Speaking rate (dil)
       - Stress of completing / arriving syl
       - Position in phrase (0.0–1.0)

     The ghost filter interpolates between
     the completing nucleus formants and
     the arriving nucleus formants, passing
     through H_FORMANTS at the midpoint.
     This is the Tonnetz traversal made
     acoustic.

  3. PHRASE-FINAL EXHALE
     After the last phoneme of every phrase,
     a ghost segment is inserted that
     interpolates from the final nucleus
     formants back to H_FORMANTS.
     Duration: longer than inter-syllable.
     Amplitude: very soft.
     This is the voice landing.
     H is what completion sounds like.

  4. VOWEL-INITIAL UNWRITTEN H
     Every word beginning with a vowel
     begins with voiced H — the
     no-constriction voiced baseline.
     This is now modeled automatically:
     when a phoneme sequence begins with
     a vowel and follows a rest or phrase
     start, a very brief ghost onset
     (5–12ms) is prepended.
     Unwritten in orthography.
     Always present as physics.

  BACKWARD COMPATIBILITY:
    All v15 arguments and calling
    conventions preserved.
    Flat phoneme lists still work.
    Ghost can be disabled:
      add_ghost=False

  Import chain:
    v16 → v15 → v14 → v13 → v9
        → v8 → v7 → v6 → v5
        → v4 → v3

  Tonnetz connection:
    from tonnetz_engine import (
        ghost_at_boundary,
        ghost_formant_interp,
        H_FORMANTS, H_BANDWIDTHS,
        VOWEL_TONNETZ,
        distance_from_H,
        GHOST_PROFILES,
    )
"""

from voice_physics_v15 import (
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
    get_f, get_b, get_f_v15, get_b_v15,
    scalar,
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
    COART_DUR_COMPRESS,
    NASAL_ANTICIPATION_GAIN,
    NASAL_ANTICIPATION_MS,
    NASAL_MURMUR_F, NASAL_MURMUR_B,
    NASAL_BLEND_PER_FORMANT,
    STOP_BLEND_PER_FORMANT,
    L_BLEND_PER_FORMANT,
    NASAL_CLOSURE_F1,
    CLOSING_PHS,
    NASAL_CLOSING_PHS,
    STOP_CLOSING_PHS,
    _coart_compress_dur,
    _coart_f_end,
    _build_trajectories_v14,
    _apply_nasal_anticipation,
    _ola_stretch,
    plan_prosody_v15,
    ph_spec_v15,
    _build_source_and_bypass_v15,
    JH_F, JH_B, CH_F, CH_B,
    AFFRICATE_F, AFFRICATE_B,
    AFFRICATE_DUR_BASE,
    JH_MAX_MS, CH_MAX_MS,
)

# Tonnetz vocal distance layer
# (added to tonnetz_engine Feb 2026)
from tonnetz_engine import (
    ghost_at_boundary,
    ghost_formant_interp,
    H_FORMANTS,
    H_BANDWIDTHS,
    VOWEL_TONNETZ,
    distance_from_H,
    GHOST_PROFILES,
    vocal_distance,
    print_vocal_distances,
)

import numpy as np
from scipy.signal import lfilter, butter
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v16'


# ============================================================
# SYLLABIFIED INPUT FORMAT
#
# v16 introduces nested phoneme lists.
# A word entry is now:
#   (word, phonemes)           flat — v15 compat
#   (word, phonemes, emph)     flat with emphasis
#   (word, syllables)          nested — v16 native
#   (word, syllables, emph)    nested with emphasis
#
# Where syllables is a list of lists:
#   [['S','T','IH','L'],...]
#
# Where phonemes is a flat list:
#   ['S','T','IH','L']
#
# _is_syllabified() detects which format.
# _flatten_syllables() extracts flat phoneme list.
# _get_syllable_boundaries() returns the sample
# indices at which syllable boundaries fall,
# for ghost insertion.
# ============================================================

def _is_syllabified(phonemes):
    """
    True if phonemes is a list of lists
    (syllabified format).
    False if it is a flat list of strings.
    """
    if not phonemes:
        return False
    return isinstance(phonemes[0], list)


def _flatten_syllables(phonemes):
    """
    Flatten syllabified or flat phoneme list
    to a flat list of ARPAbet strings.
    """
    if _is_syllabified(phonemes):
        return [ph for syl in phonemes
                for ph in syl]
    return list(phonemes)


def _get_syllable_boundary_indices(phonemes):
    """
    Given a syllabified phoneme list,
    return the cumulative phoneme counts
    at each syllable boundary.

    Example:
      [['S','T','IH','L'],['W','AH','T','ER']]
      → [4]  (boundary after phoneme index 3)

    Returns list of ints — the index of the
    LAST phoneme of each syllable except the
    last one. Ghost goes after this index.

    If flat (not syllabified), returns [].
    """
    if not _is_syllabified(phonemes):
        return []
    boundaries = []
    count = 0
    for si, syl in enumerate(phonemes[:-1]):
        count += len(syl)
        boundaries.append(count - 1)
        # count - 1 is the index of the last
        # phoneme of this syllable in the
        # flat phoneme list.
    return boundaries


def _find_nucleus(phonemes_flat):
    """
    Find the vowel nucleus of a phoneme list
    (flat). Returns the ARPAbet symbol of the
    first vowel found, or None.

    Used to identify the nucleus for ghost
    filter interpolation.
    """
    for ph in phonemes_flat:
        if ph in VOWEL_PHONEMES or \
           ph in DIPHTHONG_PHONEMES:
            return ph
    return None


# ============================================================
# SYLLABLE STRUCTURE EXTRACTION
#
# Given words_phonemes in v16 format,
# extract a list of syllable records:
#   {
#     'word':         word string
#     'word_idx':     index of word
#     'phonemes':     flat list for this syl
#     'nucleus':      ARPAbet vowel symbol
#     'stress':       0/1/2
#     'is_last_in_word': bool
#     'is_last_in_phrase': bool
#   }
#
# This is the structure that drives ghost
# placement in synth_phrase_v16.
# ============================================================

def _extract_syllable_structure(
        words_phonemes_v16):
    """
    Extract syllable records from v16 input.

    words_phonemes_v16: list of
      (word, phonemes_or_syllables)
      or (word, phonemes_or_syllables, emph)

    Returns list of syllable dicts as above.
    """
    from voice_physics_v3 import (
        STRESS_DICT, WORD_SYLLABLES
    )

    syllable_records = []

    for wi, entry in enumerate(
            words_phonemes_v16):
        word     = entry[0]
        phonemes = entry[1]

        stress_list = STRESS_DICT.get(
            word.lower(), None)

        if _is_syllabified(phonemes):
            # v16 native: syllables explicit
            syllables = phonemes
        else:
            # Flat: use WORD_SYLLABLES if
            # available, else treat as one syl
            syl_map = WORD_SYLLABLES.get(
                word.lower(), None)
            if syl_map is not None:
                syllables = syl_map
            else:
                syllables = [list(phonemes)]

        n_syls = len(syllables)
        if stress_list is None:
            stress_list = [1] * n_syls
        while len(stress_list) < n_syls:
            stress_list.append(0)

        for si, syl_phones in enumerate(
                syllables):
            nucleus = _find_nucleus(syl_phones)
            rec = {
                'word':              word,
                'word_idx':          wi,
                'phonemes':          list(syl_phones),
                'nucleus':           nucleus,
                'stress':            stress_list[si],
                'is_last_in_word':   (si == n_syls-1),
                'is_last_in_phrase': False,
            }
            syllable_records.append(rec)

    if syllable_records:
        syllable_records[-1][
            'is_last_in_phrase'] = True

    return syllable_records


# ============================================================
# GHOST SEGMENT GENERATOR
#
# Produces a micro-H segment — the Tonnetz
# traversal between two syllable nuclei,
# made acoustic.
#
# The ghost is:
#   - Aspiration noise (H = open tract)
#   - Filtered through formant interpolation
#     between F_prev (completing nucleus) and
#     F_next (arriving nucleus) via H_FORMANTS
#   - Duration and amplitude from
#     ghost_at_boundary()
#   - Envelope: short attack and release
# ============================================================

def _make_ghost_segment(
        prev_nucleus_ph,
        next_nucleus_ph,
        position_in_phrase,
        stress_prev,
        stress_next,
        arc_type,
        dil=DIL,
        phrase_final=False,
        sr=SR):
    """
    Generate one ghost segment.

    Returns float32 numpy array.
    Length = n_s determined by
    ghost_at_boundary().

    The ghost is voiceless H — open
    tract in transit. Aspiration noise
    filtered through the interpolated
    formant trajectory from F_prev
    through H_FORMANTS to F_next.

    phrase_final=True: interpolates to
    H_FORMANTS only (no F_next).
    The voice returning to rest.
    """
    dur_ms, amp = ghost_at_boundary(
        prev_nucleus_ph,
        next_nucleus_ph,
        position_in_phrase,
        stress_prev,
        stress_next,
        arc_type,
        dil=dil,
        phrase_final=phrase_final)

    n_s = max(4, int(dur_ms / 1000.0 * sr))

    # Get formant targets for filter
    if prev_nucleus_ph and \
       prev_nucleus_ph in VOWEL_F:
        F_prev = list(VOWEL_F[
            prev_nucleus_ph][0])
    else:
        F_prev = list(H_FORMANTS)

    if (not phrase_final) and \
       next_nucleus_ph and \
       next_nucleus_ph in VOWEL_F:
        F_next = list(VOWEL_F[
            next_nucleus_ph][0])
    else:
        F_next = list(H_FORMANTS)

    # Build time-varying formant arrays
    # via ghost_formant_interp from tonnetz_engine.
    # Returns list of 4 float32 arrays.
    F_arrays = ghost_formant_interp(
        F_prev, F_next, n_s, sr=sr)

    # Bandwidth arrays — use H_BANDWIDTHS
    # throughout. Ghost is open tract.
    B_arrays = [
        np.full(n_s, float(H_BANDWIDTHS[fi]),
                dtype=np.float32)
        for fi in range(4)
    ]

    # Source: aspiration noise
    # H = open glottis + open tract
    noise_raw = np.random.normal(
        0.0, 1.0, n_s).astype(np.float32)
    try:
        b, a = safe_bp(80.0, 8000.0, sr)
        noise_raw = f32(
            lfilter(b, a, noise_raw))
    except Exception:
        pass
    source = calibrate(noise_raw)

    # Run through parallel formant bank
    # (same architecture as tract() but
    #  with ghost formants)
    ghost_gains = [0.50, 0.65, 0.35, 0.18]
    result = np.zeros(n_s, dtype=np.float32)
    T = 1.0 / sr
    for fi in range(4):
        f_arr = F_arrays[fi]
        b_arr = B_arrays[fi]
        g     = ghost_gains[fi]
        out   = np.zeros(n_s,
                         dtype=np.float32)
        y1 = y2 = 0.0
        for i in range(n_s):
            fc  = max(20.0,
                      min(float(sr * 0.48),
                          float(f_arr[i])))
            bw  = max(10.0, float(b_arr[i]))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) * \
                   np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = b0*float(source[i]) + \
                  a1*y1 + a2*y2
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g

    # Amplitude envelope
    n_atk = min(int(0.005 * sr), n_s // 4)
    n_rel = min(int(0.008 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=np.float32)
    if n_atk > 0:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_rel > 0:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)

    result = result * env * amp

    # Calibrate to amp relative to
    # phrase-level signal
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = result / mx * amp

    return f32(result)


# ============================================================
# VOICED H ONSET
#
# Vowel-initial words begin with voiced H —
# the no-constriction voiced baseline.
# A brief onset (5–12ms) before the vowel
# ramps from voiced H into the vowel formants.
#
# This is PLACE 2 from h_ghost_topology.md:
# the unwritten H of "event", "always", "I".
#
# Only inserted:
#   - At phrase start if first phoneme is vowel
#   - After a rest if the next phoneme is vowel
# Not inserted word-internally (handled by
# the inter-syllable ghost).
# ============================================================

VOICED_H_DUR_MS = 8.0    # default duration
VOICED_H_AMP    = 0.042  # very soft


def _make_voiced_h_onset(
        next_nucleus_ph,
        arc_type=ARC_NORMAL,
        dil=DIL,
        sr=SR):
    """
    Generate a voiced H onset before a
    vowel-initial word.

    next_nucleus_ph: the first vowel of
    the arriving word.

    Returns float32 array ~8ms long.
    This is H voiced — the pre-vowel
    onset, not aspiration but the open
    voice before commitment arrives.
    """
    # Duration scales with Tonnetz distance
    # from H to the arriving vowel — larger
    # departure requires longer preparation.
    dist = distance_from_H(
        next_nucleus_ph or 'AH')
    dur_ms = VOICED_H_DUR_MS + \
             1.5 * dist * (dil / 6.0)
    dur_ms = float(np.clip(dur_ms, 4.0, 15.0))
    n_s    = max(4, int(
        dur_ms / 1000.0 * sr))

    if next_nucleus_ph and \
       next_nucleus_ph in VOWEL_F:
        F_next = list(VOWEL_F[
            next_nucleus_ph][0])
    else:
        F_next = list(H_FORMANTS)

    # Interpolate from H_FORMANTS to F_next
    F_arrays = []
    for fi in range(4):
        F_arrays.append(np.linspace(
            float(H_FORMANTS[fi]),
            float(F_next[fi]),
            n_s, dtype=np.float32))

    B_arrays = [
        np.full(n_s, float(H_BANDWIDTHS[fi]),
                dtype=np.float32)
        for fi in range(4)
    ]

    # Source: voiced — H baseline, glottis on
    # Simple voiced source at phrase pitch
    T      = 1.0 / sr
    raw_v  = np.zeros(n_s, dtype=np.float32)
    p      = 0.0
    pitch  = PITCH   # phrase pitch
    for i in range(n_s):
        p += pitch * T
        if p >= 1.0:
            p -= 1.0
        oq = 0.68  # open oq — breathy onset
        raw_v[i] = (
            (p/oq)*(2-p/oq) if p < oq
            else 1-(p-oq)/(1-oq+1e-9))
    raw_v  = f32(np.diff(raw_v,
                          prepend=raw_v[0]))
    raw_v  = calibrate(raw_v)

    ghost_gains = [0.50, 0.65, 0.35, 0.18]
    result = np.zeros(n_s, dtype=np.float32)
    for fi in range(4):
        f_arr = F_arrays[fi]
        b_arr = B_arrays[fi]
        g     = ghost_gains[fi]
        out   = np.zeros(n_s,
                         dtype=np.float32)
        y1 = y2 = 0.0
        for i in range(n_s):
            fc  = max(20.0, min(
                float(sr * 0.48),
                float(f_arr[i])))
            bw  = max(10.0, float(b_arr[i]))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) * \
                   np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = b0*float(raw_v[i]) + \
                  a1*y1 + a2*y2
            y2  = y1; y1  = y
            out[i] = y
        result += out * g

    # Ramp in only — the voiced H onset
    # arrives gently and flows into the vowel
    env = np.linspace(0.0, 1.0, n_s,
                      dtype=np.float32)
    result = result * env * VOICED_H_AMP
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = result / mx * VOICED_H_AMP

    return f32(result)


# ============================================================
# PHRASE SYNTHESIS v16
#
# The full ghost layer.
# Everything from v15 preserved.
# Ghost inserted at syllable boundaries.
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR,
                  arc_type=ARC_NORMAL,
                  add_breath=True,
                  add_ghost=True):
    """
    v16: The H ghost layer.

    words_phonemes: list of
      (word, phones)           flat — v15 compat
      (word, phones, emph)     flat with emphasis
      (word, syllables)        nested — v16 native
      (word, syllables, emph)  nested with emphasis

    add_ghost: bool (default True).
      False: v15 behavior, no ghost.

    All v15 arguments preserved.

    Ghost behavior:
      - Inter-syllable ghost at every
        syllable boundary in syllabified input.
      - Word-boundary ghost for flat input
        (one ghost per word boundary).
      - Phrase-final exhale after last phoneme.
      - Vowel-initial voiced H onset at phrase
        start and after rests.
    """
    # ── 1. Normalize input format ─────────────
    # Separate emphasis, build flat input for
    # plan_prosody, and record syllable structure
    # for ghost placement.

    word_emphasis        = {}
    flat_words_phonemes  = []
    syllabified_input    = []

    for entry in words_phonemes:
        if len(entry) == 3:
            word, phones, emph = entry
            word_emphasis[word] = emph
        else:
            word, phones = entry[:2]
            emph = {}

        flat_phones = _flatten_syllables(phones)
        flat_words_phonemes.append(
            (word, flat_phones))
        syllabified_input.append(
            (word, phones, emph))

    # ── 2. Extract syllable structure ─────────
    syl_records = _extract_syllable_structure(
        [(e[0], e[1]) for e in syllabified_input])

    # ── 3. Plan prosody ───────────────────────
    prosody = plan_prosody_v15(
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

        FRICS = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH'}
        if word_final and ph in FRICS:
            dur_ms = min(
                dur_ms, FINAL_FRIC_MAX_MS)

        if word_ in word_emphasis:
            emph_d  = word_emphasis[word_]
            pitch_ *= float(
                emph_d.get('f0_boost', 1.0))
            dur_ms *= float(
                emph_d.get('dur_mult',  1.0))
            amp_   *= float(
                emph_d.get('amp_boost', 1.0))

        # FIX 12A: coarticulation compression
        dur_ms = _coart_compress_dur(
            dur_ms, ph, next_ph)

        spec = ph_spec_v15(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)
        specs.append(spec)

    # ── 4. Build trajectories (FIX 12B) ───────
    F_full, B_full, _ = \
        _build_trajectories_v14(
            specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # ── 5. Build source (v15: JH/CH) ──────────
    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass_v15(
            specs, sr=sr)

    # ── 6. Tract synthesis ────────────────────
    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    # ── 7. Add bypass and buzz ────────────────
    for pos, byp in bypass_segs:
        e = min(pos + len(byp), n_total)
        out[pos:e] += byp[:e - pos]

    for pos, buz in buzz_segs:
        e = min(pos + len(buz), n_total)
        out[pos:e] += buz[:e - pos]

    # ── 8. Nasal antiformants ─────────────────
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
            seg  = out[pos:pos+n_s].copy()
            anti = np.zeros(n_s, dtype=DTYPE)
            y1 = y2 = 0.0
            for i in range(n_s):
                a2 = -np.exp(-2*np.pi*abw*T)
                a1 = (2*np.exp(-np.pi*abw*T) *
                      np.cos(2*np.pi*af*T))
                b0 = 1.0 - a1 - a2
                y  = (b0*float(seg[i]) +
                      a1*y1 + a2*y2)
                y2 = y1; y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti) * 0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:pos+n_s] = 0.0
        pos += n_s

    # ── 9. Nasal anticipation (FIX 12C) ───────
    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

    # ── 10. Amplitude envelope ────────────────
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

    # ── 11. GHOST LAYER ───────────────────────
    # Build the output with ghosts interleaved.
    # Ghosts are inserted BETWEEN syllables —
    # not inside them.
    #
    # Assembly strategy:
    #   Walk through prosody items.
    #   For each phoneme, copy its segment.
    #   At syllable boundaries: insert ghost.
    #   At word boundaries with rest: insert rest.
    #   At phrase end: insert phrase-final exhale.
    #
    # To know syllable boundaries we need to
    # map prosody items back to syllable records.
    # We do this by matching word_idx and
    # tracking position within each word.

    segs_out = []
    pos = 0

    if not add_ghost:
        # v15 behavior — no ghost, rests only
        for item, spec in zip(prosody, specs):
            n_s     = spec['n_s']
            segs_out.append(
                out[pos:pos+n_s].copy())
            rest_ms = item.get('rest_ms', 0.0)
            if rest_ms > 0:
                segs_out.append(
                    breath_rest(rest_ms, sr=sr))
            pos += n_s
    else:
        # ── Ghost-aware assembly ──────────────
        # Build syllable boundary map:
        # For each prosody item (phoneme),
        # is it the last phoneme of a syllable?
        # And if so, what is the next nucleus?

        # Build a per-phoneme list that marks
        # syllable-end boundaries from syl_records.

        # Map: flat phoneme index → (nucleus_prev,
        #                            nucleus_next,
        #                            stress_prev,
        #                            stress_next,
        #                            is_syl_end,
        #                            is_phrase_final,
        #                            has_rest_after,
        #                            rest_ms)

        # Step 1: build cumulative phoneme counts
        # per syllable record so we can find
        # which flat phoneme index = syl end.
        ph_idx_to_syl_end = {}
        ph_idx_to_syl_info = {}

        flat_ph_cursor = 0
        for sri, srec in enumerate(
                syl_records):
            n_ph_in_syl = len(srec['phonemes'])
            # Last phoneme of this syllable
            syl_end_idx = (flat_ph_cursor
                           + n_ph_in_syl - 1)
            # Nucleus of this syllable
            nuc_this = srec['nucleus'] or 'AH'
            # Nucleus of next syllable (if any)
            if sri < len(syl_records) - 1:
                nuc_next = (syl_records[sri+1]
                            ['nucleus'] or 'AH')
                stress_next = syl_records[
                    sri+1]['stress']
                is_last = False
            else:
                nuc_next    = None
                stress_next = 0
                is_last     = True

            # Only mark ghost at syllable
            # boundaries that are NOT also
            # word boundaries with a rest
            # (the rest handles that pause).
            # But we do still want a ghost
            # at word boundaries if rest is 0.
            ph_idx_to_syl_end[syl_end_idx] = {
                'nucleus_prev':  nuc_this,
                'nucleus_next':  nuc_next,
                'stress_prev':   srec['stress'],
                'stress_next':   stress_next,
                'is_phrase_final': is_last,
                'is_last_in_word': srec[
                    'is_last_in_word'],
            }
            flat_ph_cursor += n_ph_in_syl

        # Step 2: total phrase duration for
        # position_in_phrase calculation
        total_dur_ms = sum(
            item['dur_ms']
            for item in prosody)

        t_elapsed_ms = 0.0
        n_phrase_phs = len(prosody)

        # Check if first phoneme is vowel-initial
        # for voiced H onset
        first_ph = prosody[0]['ph'] if prosody \
                   else None
        first_is_vowel = (
            first_ph in VOWEL_PHONEMES or
            first_ph in DIPHTHONG_PHONEMES)

        if first_is_vowel:
            # Insert voiced H onset before
            # first phoneme
            nuc_first = first_ph
            vh = _make_voiced_h_onset(
                nuc_first,
                arc_type=arc_type,
                dil=dil, sr=sr)
            segs_out.append(vh)

        for pi, (item, spec) in enumerate(
                zip(prosody, specs)):
            n_s     = spec['n_s']
            ph      = item['ph']
            rest_ms = item.get('rest_ms', 0.0)

            # Copy phoneme segment
            segs_out.append(
                out[pos:pos+n_s].copy())

            # Position in phrase (0.0–1.0)
            pos_in_phrase = min(
                t_elapsed_ms / max(
                    total_dur_ms, 1.0),
                1.0)
            t_elapsed_ms += item['dur_ms']

            # Is this phoneme a syllable-end?
            syl_info = ph_idx_to_syl_end.get(
                pi, None)

            if syl_info is not None:
                is_phrase_final = syl_info[
                    'is_phrase_final']
                has_rest = (rest_ms > 0)

                # Phrase-final exhale:
                # always, regardless of rest
                if is_phrase_final:
                    ghost = _make_ghost_segment(
                        syl_info['nucleus_prev'],
                        None,
                        pos_in_phrase,
                        syl_info['stress_prev'],
                        0,
                        arc_type,
                        dil=dil,
                        phrase_final=True,
                        sr=sr)
                    segs_out.append(ghost)

                elif has_rest:
                    # At word boundaries with rest:
                    # a shorter ghost THEN the rest.
                    # The ghost is the coda exhale.
                    # The rest is the breath.
                    ghost = _make_ghost_segment(
                        syl_info['nucleus_prev'],
                        syl_info['nucleus_next'],
                        pos_in_phrase,
                        syl_info['stress_prev'],
                        syl_info['stress_next'],
                        arc_type,
                        dil=dil,
                        phrase_final=False,
                        sr=sr)
                    segs_out.append(ghost)
                    segs_out.append(
                        breath_rest(
                            rest_ms, sr=sr))

                    # After rest, if next phoneme
                    # is vowel-initial: voiced H
                    next_pi = pi + 1
                    if next_pi < n_phrase_phs:
                        next_ph_sym = prosody[
                            next_pi]['ph']
                        if (next_ph_sym in
                                VOWEL_PHONEMES or
                                next_ph_sym in
                                DIPHTHONG_PHONEMES):
                            vh = _make_voiced_h_onset(
                                next_ph_sym,
                                arc_type=arc_type,
                                dil=dil, sr=sr)
                            segs_out.append(vh)

                else:
                    # Inter-syllable ghost
                    # (no rest, not phrase final)
                    if syl_info['nucleus_next'] \
                       is not None:
                        ghost = _make_ghost_segment(
                            syl_info['nucleus_prev'],
                            syl_info['nucleus_next'],
                            pos_in_phrase,
                            syl_info['stress_prev'],
                            syl_info['stress_next'],
                            arc_type,
                            dil=dil,
                            phrase_final=False,
                            sr=sr)
                        segs_out.append(ghost)

            elif rest_ms > 0:
                # Not a syl-end in our records
                # but has a rest (flat input,
                # word-boundary rest).
                # Treat as word boundary:
                # ghost + rest.
                # Find nearest vowel for nucleus
                nuc_prev = None
                for pj in range(pi, -1, -1):
                    pph = prosody[pj]['ph']
                    if pph in VOWEL_PHONEMES or \
                       pph in DIPHTHONG_PHONEMES:
                        nuc_prev = pph
                        break
                nuc_next = None
                for pj in range(pi+1,
                                n_phrase_phs):
                    pph = prosody[pj]['ph']
                    if pph in VOWEL_PHONEMES or \
                       pph in DIPHTHONG_PHONEMES:
                        nuc_next = pph
                        break

                if nuc_prev is not None:
                    ghost = _make_ghost_segment(
                        nuc_prev or 'AH',
                        nuc_next,
                        pos_in_phrase,
                        1, 1,
                        arc_type,
                        dil=dil,
                        phrase_final=False,
                        sr=sr)
                    segs_out.append(ghost)
                segs_out.append(
                    breath_rest(rest_ms, sr=sr))

            pos += n_s

    # ── 12. Concatenate and normalize ─────────
    final = f32(np.concatenate(segs_out))
    final = _normalize_phrase(
        final, specs, prosody, sr=sr)

    # ── 13. Breath onset ──────────────────────
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
# CONVENIENCE
# ============================================================

def save(name, sig, room=True,
          rt60=1.5, dr=0.50, sr=SR):
    sig = f32(sig)
    if room:
        sig = apply_room(
            sig, rt60=rt60, dr=dr, sr=sr)
    write_wav(
        f"output_play/{name}.wav", sig, sr)
    dur = len(sig) / sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN — diagnostics for ghost layer
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v16")
    print("FIX 14: The H Ghost Layer")
    print()
    print("  Inter-syllable ghost: Tonnetz")
    print("    distance → duration")
    print("    Arc type → ghost signature")
    print("    Ghost filter: F_prev → H → F_next")
    print()
    print("  Phrase-final exhale:")
    print("    After last phoneme.")
    print("    Voice returning to H.")
    print("    Completion sounds like H.")
    print()
    print("  Vowel-initial voiced H onset:")
    print("    'event', 'already', 'I'")
    print("    Unwritten. Always present.")
    print("=" * 52)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Tonnetz distance table:")
    print_vocal_distances()

    # ── DIAGNOSTIC 1: ghost vs no ghost ────────
    print("  Diagnostic 1: ghost on/off comparison")
    PHRASE_BASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', [['AO','L'],
                     ['R', 'EH'],
                     ['D', 'IY']]),
        ('here',    ['H',  'IY', 'R']),
    ]

    seg_no_ghost = synth_phrase(
        PHRASE_BASE,
        punctuation='.',
        arc_type=ARC_NORMAL,
        add_ghost=False)
    save("v16_the_voice_no_ghost",
         seg_no_ghost, rt60=1.5, dr=0.50)

    seg_ghost = synth_phrase(
        PHRASE_BASE,
        punctuation='.',
        arc_type=ARC_NORMAL,
        add_ghost=True)
    save("v16_the_voice_with_ghost",
         seg_ghost, rt60=1.5, dr=0.50)

    print("    → listen for the carrying-through")
    print("      between syllables in _with_ghost")
    print()

    # ── DIAGNOSTIC 2: arc type comparison ──────
    print("  Diagnostic 2: arc type signatures")
    ARC_PHRASE = [
        ('I',    ['AY']),
        ('am',   ['AE', 'M']),
        ('here', ['H',  'IY', 'R']),
    ]
    for arc, label in [
        (ARC_NORMAL,  'normal'),
        (ARC_GRIEF,   'grief'),
        (ARC_CONTAIN, 'contain'),
        (ARC_EUREKA,  'eureka'),
    ]:
        seg = synth_phrase(
            ARC_PHRASE,
            punctuation='.',
            arc_type=arc)
        save(f"v16_i_am_here_{label}",
             seg, rt60=1.4, dr=0.52)
    print("    → same words, different ghosts")
    print("      grief: long soft between beats")
    print("      contain: ghost cut short")
    print("      eureka: ghost gathers before HERE")
    print()

    # ── DIAGNOSTIC 3: already syllabified ──────
    print("  Diagnostic 3: 'already' syllabified")
    print("    Flat:       ['AO','L','R','EH','D','IY']")
    print("    Syllabified:[['AO','L'],['R','EH'],['D','IY']]")
    print("    Stressed syl: 2nd — R EH")
    print()

    seg_flat = synth_phrase(
        [('already', ['AO','L','R',
                      'EH','D','IY'])],
        punctuation='.',
        add_ghost=True)
    save("v16_already_flat",
         seg_flat, rt60=0.8, dr=0.65)

    seg_syl = synth_phrase(
        [('already', [['AO','L'],
                      ['R','EH'],
                      ['D','IY']])],
        punctuation='.',
        add_ghost=True)
    save("v16_already_syllabified",
         seg_syl, rt60=0.8, dr=0.65)

    for label, sig in [
        ('flat', seg_flat),
        ('syllabified', seg_syl),
    ]:
        seg_slow = _ola_stretch(
            synth_phrase(
                [('already',
                  ['AO','L','R','EH','D','IY']
                  if label == 'flat'
                  else [['AO','L'],
                        ['R','EH'],
                        ['D','IY']])],
                punctuation='.',
                add_breath=False,
                add_ghost=True),
            factor=4.0)
        save(f"v16_already_{label}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → flat: no inter-syllable ghost")
    print("      syllabified: ghost between")
    print("      AO-L | R-EH | D-IY")
    print("      hear the seams open up")
    print()

    # ── DIAGNOSTIC 4: event / evening ──────────
    print("  Diagnostic 4: vowel-initial H onset")
    print("    'event', 'evening' — unwritten H")
    print()

    for word, phones in [
        ('event',   ['IH', 'V', 'EH', 'N', 'T']),
        ('evening', ['IY', 'V', 'IH', 'N',
                     'IH', 'NG']),
        ('already', ['AO', 'L', 'R',
                     'EH', 'D', 'IY']),
        ('I',       ['AY']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v16_{word}_vowel_onset",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=True),
            factor=4.0)
        save(f"v16_{word}_vowel_onset_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → slow: hear the brief H onset")
    print("      before the vowel body begins")
    print()

    # ── DIAGNOSTIC 5: phrase-final exhale ──────
    print("  Diagnostic 5: phrase-final exhale")
    print("    'here' — voice returns to H")
    print()

    for arc, label in [
        (ARC_NORMAL,  'normal'),
        (ARC_GRIEF,   'grief'),
    ]:
        seg = synth_phrase(
            [('here', ['H', 'IY', 'R'])],
            punctuation='.',
            arc_type=arc,
            add_ghost=True)
        save(f"v16_here_exhale_{label}",
             seg, rt60=1.0, dr=0.60)

    print("    → grief: longer, softer exhale")
    print("      normal: brief, clean landing")
    print()

    # ── DIAGNOSTIC 6: the full sentence ────────
    print("  Diagnostic 6: full sentence")
    print("    syllabified + ghost + all arcs")
    print()

    FULL_PHRASE_SYL = [
        ('the',     ['DH', 'AH']),
        ('voice',   [['V', 'OY'],
                     ['S']]),
        ('was',     ['W', 'AH', 'Z']),
        ('already', [['AO', 'L'],
                     ['R',  'EH'],
                     ['D',  'IY']]),
        ('here',    ['H', 'IY', 'R']),
    ]

    for arc, label in [
        (ARC_NORMAL,  'normal'),
        (ARC_GRIEF,   'grief'),
        (ARC_CONTAIN, 'contain'),
    ]:
        seg = synth_phrase(
            FULL_PHRASE_SYL,
            punctuation='.',
            arc_type=arc,
            add_ghost=True)
        save(f"v16_the_voice_{label}",
             seg, rt60=1.5, dr=0.50)

    print()
    print("=" * 52)
    print()
    print("  PLAY ORDER:")
    print()
    print("  1. Ghost on vs off:")
    print("  afplay output_play/"
          "v16_the_voice_no_ghost.wav")
    print("  afplay output_play/"
          "v16_the_voice_with_ghost.wav")
    print()
    print("  2. Arc signatures — same words:")
    print("  afplay output_play/"
          "v16_i_am_here_normal.wav")
    print("  afplay output_play/"
          "v16_i_am_here_grief.wav")
    print("  afplay output_play/"
          "v16_i_am_here_contain.wav")
    print("  afplay output_play/"
          "v16_i_am_here_eureka.wav")
    print()
    print("  3. Syllabification — already:")
    print("  afplay output_play/"
          "v16_already_flat_slow.wav")
    print("  afplay output_play/"
          "v16_already_syllabified_slow.wav")
    print()
    print("  4. Vowel-initial H onset:")
    print("  afplay output_play/"
          "v16_event_vowel_onset_slow.wav")
    print("  afplay output_play/"
          "v16_I_vowel_onset_slow.wav")
    print()
    print("  5. Phrase-final exhale:")
    print("  afplay output_play/"
          "v16_here_exhale_grief.wav")
    print("  afplay output_play/"
          "v16_here_exhale_normal.wav")
    print()
    print("  6. Full sentence arc comparison:")
    print("  afplay output_play/"
          "v16_the_voice_normal.wav")
    print("  afplay output_play/"
          "v16_the_voice_grief.wav")
    print("  afplay output_play/"
          "v16_the_voice_contain.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  Ghost on/off:")
    print("    No ghost: phonemes arrive")
    print("    cleanly. Efficient. Robotic.")
    print("    Ghost: the carrying-through.")
    print("    The voice between intentions.")
    print()
    print("  Arc grief vs contain:")
    print("    Grief: the ghost lingers.")
    print("    The voice does not want")
    print("    to leave H to start the")
    print("    next beat.")
    print("    Contain: the ghost is cut.")
    print("    The beat ends but does")
    print("    not exhale.")
    print()
    print("  Already syllabified slow:")
    print("    Flat: one continuous word.")
    print("    Syllabified: three beats.")
    print("    AO-L | R-EH | D-IY")
    print("    Hear the seams between them.")
    print("    That is the ghost.")
    print()
    print("  Event vowel onset slow:")
    print("    The H before the IH.")
    print("    Not spelled. Always there.")
    print("    The voice arriving before")
    print("    the vowel commits.")
    print()
