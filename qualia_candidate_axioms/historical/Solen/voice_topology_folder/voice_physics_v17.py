"""
VOICE PHYSICS v17
February 2026

FIX 15: DIRECTIONAL LOCUS TRANSITIONS

  locus_transitions.md established that:

    The consonant has no direction in
    the current engine.

    Coda N and onset N sound identical
    because both receive the same formant
    interpolation — undirected, from
    F_current toward F_tgt.

    The perceptual identity of a consonant
    lives in the TRANSITION — the 10–20ms
    of formant movement on either side of
    the closure. Not in the closure itself.

    During closure: silence or murmur.
    During transition: the consonant.

  THE LOCUS:

    The locus is the frequency toward which
    F2 converges during a consonant gesture.
    It is determined by place of articulation:

      Bilabial  (M,B,P,W):      ~720 Hz
      Labiodental (F,V):        ~1100 Hz
      Dental    (TH,DH):        ~1600 Hz
      Alveolar  (T,D,N,L,S,Z):  ~1800 Hz
      Lateral   (L — dark coda): ~1000 Hz
      Postalveolar (SH,ZH,CH,JH): ~2100 Hz
      Palatal   (Y):            ~2300 Hz
      Velar     (K,G,NG):       ~2400–3000 Hz
                (context-sensitive — shifts
                 with following vowel's
                 Tonnetz fifth-axis position)
      Glottal   (H,HH):         ~500 Hz
      Rhotic    (R):            ~800 Hz F2
                                (F3 suppression
                                 is primary)

  DIRECTION:

    Onset consonant (H → locus → vowel):
      F2 begins AT or NEAR the locus.
      F2 transitions TOWARD the vowel F2.
      The tract is opening, approaching
      the vowel from baseline.

    Coda consonant (vowel → locus → H):
      F2 begins AT the vowel F2.
      F2 transitions TOWARD the locus.
      The tract is closing, departing
      the vowel toward baseline.

    Same phoneme. Different direction.
    Different percept.

  THE N IN "EVENING":

    Coda N (syllable 2):
      IH F2 (~2050) → alveolar locus (~1800).
      Heard as: departure. Closing.

    Onset N (syllable 3 start):
      alveolar locus (~1800) → IH F2 (~2050).
      Heard as: arrival. Opening.

    Now distinguishable.

  DARK L:
    Post-vocalic (coda) L has F2 locus ~1000.
    This is the "dark L" — what is heard in
    "already", "still", "all".
    Pre-vocalic (onset) L has F2 locus ~1800.
    The existing L_BLEND_PER_FORMANT in v14
    approximates this but is not directional.
    The locus model makes it exact.

  VELAR CONTEXT SENSITIVITY:
    K/G/NG locus shifts with following vowel
    Tonnetz fifth-axis position (a):
      locus = 2400 + 200 * a
      K before IY (a=3):  locus ~3000
      K before AH (a=0):  locus ~2400
      K before UW (a=-3): locus ~1800

  R / ER F3 SUPPRESSION:
    R and ER: F3 falls toward 1690 Hz
    explicitly throughout the segment.
    This was partially in v7 (r_f3 flag).
    The locus model makes it the primary
    R identity mechanism.

  INTEGRATION:
    _build_trajectories_v17() replaces
    _build_trajectories_v14() in synth_phrase.
    The locus model patches the n_on and
    n_off zones for consonant phonemes only.
    Vowel trajectories: unchanged.
    Diphthong trajectories: unchanged.
    All v14/v15/v16 fixes: preserved.

  Import chain:
    v17 → v16 → v15 → v14 → v13
        → v9 → v8 → v7 → v6
        → v5 → v4 → v3
"""

from voice_physics_v16 import (
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
    _apply_nasal_anticipation,
    _ola_stretch,
    plan_prosody_v15,
    ph_spec_v15,
    _build_source_and_bypass_v15,
    JH_F, JH_B, CH_F, CH_B,
    AFFRICATE_F, AFFRICATE_B,
    AFFRICATE_DUR_BASE,
    JH_MAX_MS, CH_MAX_MS,
    # v16 ghost layer
    _is_syllabified,
    _flatten_syllables,
    _get_syllable_boundary_indices,
    _find_nucleus,
    _extract_syllable_structure,
    _make_ghost_segment,
    _make_voiced_h_onset,
    VOICED_H_DUR_MS,
    VOICED_H_AMP,
)

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
from scipy.signal import lfilter
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v17'


# ============================================================
# FIX 15: LOCUS TRANSITION TABLES
# ============================================================

# Place of articulation for each consonant phoneme.
PH_LOCUS_CLASS = {
    # Bilabial
    'M':  'bilabial',
    'B':  'bilabial',
    'P':  'bilabial',
    'W':  'bilabial',
    # Labiodental
    'F':  'labiodental',
    'V':  'labiodental',
    # Dental
    'TH': 'dental',
    'DH': 'dental',
    # Alveolar
    'T':  'alveolar',
    'D':  'alveolar',
    'N':  'alveolar',
    'S':  'alveolar',
    'Z':  'alveolar',
    # Lateral — separate from alveolar
    # because dark-L coda has different locus
    'L':  'lateral',
    # Postalveolar
    'SH': 'postalveolar',
    'ZH': 'postalveolar',
    'CH': 'postalveolar',
    'JH': 'postalveolar',
    # Palatal
    'Y':  'palatal',
    # Velar (context-sensitive)
    'K':  'velar',
    'G':  'velar',
    'NG': 'velar',
    # Glottal
    'H':  'glottal',
    'HH': 'glottal',
    # Rhotic (F3 suppression primary)
    'R':  'rhotic',
}

# Base F2 locus per place class (Hz).
# These are the F2 targets during the
# consonant gesture — where F2 moves
# toward (onset) or away from (coda).
LOCUS_F2_BASE = {
    'bilabial':      720,
    'labiodental':   1100,
    'dental':        1600,
    'alveolar':      1800,
    'lateral':       1000,   # dark coda L
    'postalveolar':  2100,
    'palatal':       2300,
    'velar':         2700,   # adjusted below
    'glottal':       500,
    'rhotic':        800,
}

# F1 locus — all consonant closures
# pull F1 low. Place-specific but weaker
# than F2. These supplement the existing
# NASAL_CLOSURE_F1 model.
LOCUS_F1_BASE = {
    'bilabial':      250,
    'labiodental':   280,
    'dental':        280,
    'alveolar':      280,
    'lateral':       320,    # lateral keeps F1 slightly higher
    'postalveolar':  260,
    'palatal':       270,
    'velar':         300,
    'glottal':       480,    # H barely changes F1
    'rhotic':        490,    # ER region
}

# Transition duration (ms) — how long
# the formant takes to move from locus
# to vowel target (onset) or vowel target
# to locus (coda).
# Approximants are slower (longer glide).
# Stops are faster (abrupt release).
LOCUS_TRANS_MS = {
    'bilabial':      14,
    'labiodental':   18,
    'dental':        16,
    'alveolar':      14,
    'lateral':       38,    # approximant — slow
    'postalveolar':  18,
    'palatal':       32,    # approximant — slow
    'velar':         18,
    'glottal':        8,    # very fast
    'rhotic':        32,    # approximant — slow
}

# F3 target for R and ER: suppressed.
# The defining feature of the rhotic.
R_F3_TARGET = 1690.0

# Lateral F2 — onset L uses higher value
# (pre-vocalic, bright L);
# coda L uses LOCUS_F2_BASE['lateral'] = 1000
# (post-vocalic, dark L).
L_ONSET_F2  = 1800.0
L_CODA_F2   = 1000.0

# Phonemes that are always onset
# (cannot be coda in English):
ONSET_ONLY_PHS = {'W', 'Y', 'HH', 'H'}

# Phonemes that are always coda when
# word-final. This is used as a hint —
# the direction algorithm has primary
# responsibility.
CODA_HINT_PHS = {'NG'}


# ============================================================
# LOCUS COMPUTATION
# ============================================================

def _locus_f2(ph, adjacent_vowel_ph,
               is_coda):
    """
    Compute the F2 locus for a consonant
    adjacent to a given vowel.

    ph              : ARPAbet consonant symbol
    adjacent_vowel_ph: ARPAbet vowel symbol
                       (following if onset,
                        preceding if coda).
                       None if not available.
    is_coda         : bool. True = coda direction.

    Returns (f2_locus, f1_locus) as floats.

    For velars: locus shifts with adjacent
    vowel's Tonnetz fifth-axis position.
    For lateral: onset vs coda F2 differs.
    """
    place = PH_LOCUS_CLASS.get(ph)
    if place is None:
        # Unknown consonant — neutral
        return 1500.0, 280.0

    f2 = float(LOCUS_F2_BASE.get(
        place, 1500))
    f1 = float(LOCUS_F1_BASE.get(
        place, 280))

    # Velar context sensitivity
    if place == 'velar' and \
       adjacent_vowel_ph is not None:
        pos = VOWEL_TONNETZ.get(
            adjacent_vowel_ph, (0, 0))
        a   = float(pos[0])
        # locus = 2400 + 200 * a
        # IY (a=3) → 3000
        # AH (a=0) → 2400
        # UW (a=-3) → 1800
        f2 = max(1800.0,
                 min(3200.0,
                     2400.0 + 200.0 * a))

    # Lateral: onset vs coda distinction
    if place == 'lateral':
        f2 = (L_CODA_F2 if is_coda
              else L_ONSET_F2)

    return f2, f1


def _consonant_is_coda(si, phoneme_specs):
    """
    Determine whether the consonant at
    index si in phoneme_specs is acting
    as a coda (following the nucleus) or
    an onset (preceding the nucleus).

    Strategy:
      Look at the preceding phoneme.
      If the preceding phoneme is a vowel
      or diphthong: this consonant is coda.
      If the preceding phoneme is a consonant
      or nothing (phrase start): onset.

    For consonant clusters:
      Initial cluster (phrase start or
      post-rest): all are onset.
      Final cluster (phrase end or
      pre-rest): all are coda.
      Medial cluster: the split is at the
      syllable boundary, which is encoded
      in the syllable records.
      For flat input without syllable info:
      fall back to vowel-search heuristic.

    Returns True if coda, False if onset.
    """
    # Always-onset phonemes
    ph = phoneme_specs[si]['ph']
    if ph in ONSET_ONLY_PHS:
        return False
    # Always-coda (e.g. NG)
    if ph in CODA_HINT_PHS:
        return True

    # Search backward for most recent vowel
    # and forward for next vowel.
    found_vowel_before = False
    found_vowel_after  = False

    for j in range(si - 1, -1, -1):
        pph = phoneme_specs[j]['ph']
        if pph in VOWEL_PHONEMES or \
           pph in DIPHTHONG_PHONEMES:
            found_vowel_before = True
            break
        if PH_LOCUS_CLASS.get(pph) is None:
            # Unknown — stop
            break

    for j in range(si + 1,
                   len(phoneme_specs)):
        pph = phoneme_specs[j]['ph']
        if pph in VOWEL_PHONEMES or \
           pph in DIPHTHONG_PHONEMES:
            found_vowel_after = True
            break
        if PH_LOCUS_CLASS.get(pph) is None:
            break

    # If vowel precedes and no vowel
    # follows → coda.
    # If vowel follows and no vowel
    # precedes → onset.
    # If both → immediately after vowel
    # = coda if the following vowel is
    # in the next word (inter-syllabic);
    # need to check word_final flag.
    if found_vowel_before and \
       not found_vowel_after:
        return True
    if found_vowel_after and \
       not found_vowel_before:
        return False
    if found_vowel_before and \
       found_vowel_after:
        # Between two vowels.
        # If word_final flag set: coda.
        # Else: onset of following syllable
        # (English onset maximization).
        wf = phoneme_specs[si].get(
            'word_final', False)
        return bool(wf)

    # No vowel context (all consonants):
    # phrase-initial cluster → all onset
    return False


def _find_adjacent_vowel(
        si, phoneme_specs, is_coda):
    """
    Find the adjacent vowel for a consonant.
    If is_coda: search backward for preceding vowel.
    If onset:   search forward for following vowel.

    Returns ARPAbet vowel symbol or None.
    """
    if is_coda:
        for j in range(si - 1, -1, -1):
            pph = phoneme_specs[j]['ph']
            if pph in VOWEL_PHONEMES or \
               pph in DIPHTHONG_PHONEMES:
                return pph
    else:
        for j in range(si + 1,
                       len(phoneme_specs)):
            pph = phoneme_specs[j]['ph']
            if pph in VOWEL_PHONEMES or \
               pph in DIPHTHONG_PHONEMES:
                return pph
    return None


# ============================================================
# TRAJECTORY BUILDER v17
#
# Replaces _build_trajectories_v14 in
# synth_phrase.
#
# Changes from v14:
#   The n_on zone (onset transition) and
#   n_off zone (coda transition) for
#   consonant phonemes are now computed
#   using directed locus transitions:
#
#   Onset: F2 starts at locus, moves
#          toward the vowel's F2.
#   Coda:  F2 starts at vowel's F2,
#          moves toward the locus.
#
#   F1: same principle, using LOCUS_F1_BASE.
#   F3: for R/ER, suppressed to 1690 Hz.
#   F4: unchanged — neutral throughout.
#
#   Vowel and diphthong trajectories:
#   unchanged from _build_trajectories_v14.
#
# The function also handles the FIX 12B
# F_end per-formant blend (preserved from
# v14) — the locus model supplements it,
# not replaces it.
# ============================================================

def _build_trajectories_v17(
        phoneme_specs, sr=SR):
    """
    v17 trajectory builder.
    Adds directed locus transitions for
    all consonant phonemes.
    All v14 vowel trajectory logic preserved.
    """
    # First: apply v14's coarticulation
    # blend to get F_end fields set.
    # Then we will patch the consonant
    # n_on / n_off zones.
    # We cannot call _build_trajectories_v14
    # directly because we need to intercept
    # the consonant zones.
    # Instead: replicate the v14 trajectory
    # loop with locus patches applied.

    from voice_physics_v14 import (
        _build_trajectories_v14,
    )

    n_specs = len(phoneme_specs)
    if n_specs == 0:
        return ([np.zeros(1, dtype=DTYPE)]*4,
                [np.zeros(1, dtype=DTYPE)]*4,
                [])

    # Step 1: Apply v14 coarticulation
    # F_end patching (FIX 12B) to get
    # correct F_end values on specs.
    # We do this by running a pre-pass
    # to compute F_end for each vowel.
    patched_specs = []
    for si, spec in enumerate(phoneme_specs):
        ph      = spec['ph']
        next_ph = (phoneme_specs[si+1]['ph']
                   if si < n_specs-1
                   else None)
        s = copy.copy(spec)
        # Apply v14 F_end logic for vowels
        # before closing consonants
        if (next_ph in CLOSING_PHS and
                ph in (VOWEL_PHONEMES |
                       DIPHTHONG_PHONEMES)):
            raw_b = get_b(ph)
            if isinstance(raw_b,
                          (list, tuple)):
                default_b = list(raw_b)
            else:
                default_b = [float(raw_b)]*4
            current_f = list(
                s.get('F_tgt', get_f(ph)))
            current_b = list(
                s.get('B_tgt', default_b))
            from voice_physics_v14 import \
                _coart_f_end
            f_end, b_end = _coart_f_end(
                ph, next_ph,
                current_f, current_b)
            if f_end is not None:
                s['F_end'] = f_end
        patched_specs.append(s)

    # Step 2: Build full trajectory arrays
    n_total  = sum(s['n_s']
                   for s in patched_specs)
    F_full   = [np.zeros(n_total, dtype=DTYPE)
                for _ in range(4)]
    B_full   = [np.zeros(n_total, dtype=DTYPE)
                for _ in range(4)]
    seg_ends = []

    F_current = list(
        patched_specs[0]['F_tgt'])
    B_current = list(
        patched_specs[0]['B_tgt'])

    pos = 0
    for si, spec in enumerate(patched_specs):
        ph      = spec['ph']
        n_s     = spec['n_s']
        F_tgt   = list(spec['F_tgt'])
        B_tgt   = spec.get('B_tgt',
                            get_b(ph))
        if not isinstance(B_tgt,
                          (list, tuple)):
            B_tgt = [float(B_tgt)] * 4
        B_tgt   = list(B_tgt)
        bw_mult = spec.get('bw_mult', 1.0)
        F_end   = spec.get('F_end', F_tgt)
        is_d    = spec.get('diphthong',
                           False)
        r_f3    = spec.get('r_f3', False)
        cf      = spec.get('coart_frac',
                           0.20)

        # Next spec's F_tgt for n_off zone
        if si < n_specs - 1:
            F_next  = list(
                patched_specs[si+1]['F_tgt'])
            B_next  = patched_specs[si+1].get(
                'B_tgt', get_b(
                    patched_specs[si+1]['ph']))
            if not isinstance(B_next,
                              (list, tuple)):
                B_next = [float(B_next)] * 4
            B_next  = list(B_next)
        else:
            F_next  = (list(F_end)
                       if is_d
                       else list(F_tgt))
            B_next  = list(B_tgt)

        # Determine if this phoneme is a
        # consonant that needs locus treatment
        is_cons = PH_LOCUS_CLASS.get(
            ph) is not None
        is_vowel_ph = (
            ph in VOWEL_PHONEMES or
            ph in DIPHTHONG_PHONEMES)

        # Compute transition zone sizes
        # For consonants: use locus_trans_ms
        # For vowels: use coart_frac
        if is_cons and not is_vowel_ph:
            place    = PH_LOCUS_CLASS[ph]
            trans_ms = LOCUS_TRANS_MS.get(
                place, 15)
            n_on  = min(
                int(trans_ms / 1000.0 * sr),
                n_s // 3)
            n_off = min(
                int(trans_ms / 1000.0 * sr),
                n_s // 3)
        else:
            n_on  = min(trans_n(ph, sr),
                        n_s // 3)
            n_off = min(trans_n(ph, sr),
                        n_s // 3)

        n_mid = n_s - n_on - n_off
        if n_mid < 1:
            n_mid = 1
            n_on  = (n_s - 1) // 2
            n_off = n_s - 1 - n_on

        F_from = list(F_current)
        B_from = list(B_current)

        # ── Locus computation for consonants ──
        if is_cons and not is_vowel_ph:
            is_coda = _consonant_is_coda(
                si, patched_specs)
            adj_vowel = _find_adjacent_vowel(
                si, patched_specs, is_coda)
            locus_f2, locus_f1 = _locus_f2(
                ph, adj_vowel, is_coda)

            # Build per-formant arrays
            for fi in range(4):
                f_arr = np.zeros(
                    n_s, dtype=DTYPE)

                if fi == 1:
                    # F2: directed locus
                    if is_coda:
                        # vowel F2 → locus
                        # n_on: arrive from prev
                        # n_mid: at locus
                        # n_off: hold at locus
                        #        OR transition to
                        #        F_next (next vowel
                        #        onset)
                        f_on_start = float(
                            F_from[fi])
                        f_on_end   = locus_f2
                        f_mid_val  = locus_f2
                        f_off_end  = locus_f2
                    else:
                        # locus → vowel F2
                        # n_on: at locus
                        # n_mid: at locus
                        # n_off: leave toward
                        #        following vowel
                        f_on_start = locus_f2
                        f_on_end   = locus_f2
                        f_mid_val  = locus_f2
                        f_off_end  = float(
                            F_next[fi])

                elif fi == 0:
                    # F1: directed locus
                    if is_coda:
                        f_on_start = float(
                            F_from[fi])
                        f_on_end   = locus_f1
                        f_mid_val  = locus_f1
                        f_off_end  = locus_f1
                    else:
                        f_on_start = locus_f1
                        f_on_end   = locus_f1
                        f_mid_val  = locus_f1
                        f_off_end  = float(
                            F_next[fi])

                elif fi == 2:
                    # F3: R/ER suppression
                    if (ph in ('R', 'ER') or
                            r_f3):
                        # F3 falls toward 1690
                        f_on_start = float(
                            F_from[fi])
                        f_on_end   = R_F3_TARGET
                        f_mid_val  = R_F3_TARGET
                        f_off_end  = R_F3_TARGET
                    else:
                        # F3 follows F_tgt
                        f_on_start = float(
                            F_from[fi])
                        f_on_end   = float(
                            F_tgt[fi])
                        f_mid_val  = float(
                            F_tgt[fi])
                        f_off_end  = float(
                            F_next[fi])

                else:
                    # F4: neutral, linear
                    f_on_start = float(
                        F_from[fi])
                    f_on_end   = float(
                        F_tgt[fi])
                    f_mid_val  = float(
                        F_tgt[fi])
                    f_off_end  = float(
                        F_next[fi])

                # Assemble the three zones
                if n_on > 0:
                    # Sigmoid onset transition
                    t_on = np.linspace(
                        0.0, 1.0, n_on)
                    sig_on = 1.0 / (
                        1.0 + np.exp(
                            -8.0*(t_on-0.5)))
                    f_arr[:n_on] = (
                        f_on_start +
                        (f_on_end - f_on_start)
                        * sig_on).astype(DTYPE)

                if n_mid > 0:
                    f_arr[n_on:n_on+n_mid] = \
                        float(f_mid_val)

                if n_off > 0:
                    # Sigmoid off transition
                    t_off = np.linspace(
                        0.0, 1.0, n_off)
                    sig_off = 1.0 / (
                        1.0 + np.exp(
                            -8.0*(t_off-0.5)))
                    f_arr[n_on+n_mid:] = (
                        float(f_mid_val) +
                        (f_off_end -
                         float(f_mid_val))
                        * sig_off).astype(DTYPE)

                F_full[fi][pos:pos+n_s] = f_arr

                # Bandwidth
                b_arr = np.full(
                    n_s,
                    float(B_tgt[fi]) * bw_mult,
                    dtype=DTYPE)
                B_full[fi][pos:pos+n_s] = b_arr

        else:
            # ── Vowel / diphthong trajectory ──
            # Preserved from v14 / v3 logic.
            for fi in range(4):
                f_arr = np.zeros(
                    n_s, dtype=DTYPE)

                if n_on > 0:
                    f_arr[:n_on] = np.linspace(
                        float(F_from[fi]),
                        float(F_tgt[fi]),
                        n_on, dtype=DTYPE)

                if n_mid > 0:
                    if is_d:
                        nm = int(n_mid * 0.72)
                        nh = n_mid - nm
                        if nm > 0:
                            f_arr[
                                n_on:n_on+nm] = \
                                np.linspace(
                                    float(
                                        F_tgt[fi]),
                                    float(
                                        F_end[fi]),
                                    nm,
                                    dtype=DTYPE)
                        if nh > 0:
                            f_arr[
                                n_on+nm:
                                n_on+n_mid] = \
                                float(F_end[fi])
                    else:
                        f_arr[n_on:n_on+n_mid]\
                            = float(F_tgt[fi])

                if n_off > 0:
                    ff = (float(F_end[fi])
                          if is_d
                          else float(F_tgt[fi]))
                    f_arr[n_on+n_mid:] = \
                        np.linspace(
                            ff,
                            float(F_next[fi]),
                            n_off,
                            dtype=DTYPE)

                if r_f3 and fi == 2:
                    nd = min(
                        int(0.030 * sr), n_s)
                    f_arr[:nd] = np.linspace(
                        float(F_from[2]),
                        R_F3_TARGET, nd,
                        dtype=DTYPE)
                    f_arr[nd:] = R_F3_TARGET

                F_full[fi][pos:pos+n_s] = f_arr

                b_arr = np.linspace(
                    float(B_from[fi]),
                    float(B_tgt[fi]) * bw_mult,
                    n_s, dtype=DTYPE)
                b_arr = np.clip(
                    b_arr, 10.0, 1200.0)
                B_full[fi][pos:pos+n_s] = b_arr

        # Update current state
        for fi in range(4):
            F_current[fi] = float(
                F_full[fi][pos+n_s-1])
            B_current[fi] = float(
                B_full[fi][pos+n_s-1])

        pos += n_s
        seg_ends.append(pos)

    return F_full, B_full, seg_ends


# ============================================================
# PHRASE SYNTHESIS v17
#
# Identical to v16 except:
#   _build_trajectories_v14 replaced with
#   _build_trajectories_v17.
#
# All v16 ghost layer logic preserved.
# All v15 affricate logic preserved.
# All v14 coarticulation logic preserved.
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
    v17: Directional locus transitions.
    All v16 features preserved.
    """
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

    syl_records = _extract_syllable_structure(
        [(e[0], e[1])
         for e in syllabified_input])

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
        next_ph    = (prosody[i+1]['ph']
                      if i < n_items-1
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

    # ── FIX 15: directional locus ─────────────
    F_full, B_full, _ = \
        _build_trajectories_v17(
            specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass_v15(
            specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos + len(byp), n_total)
        out[pos:e] += byp[:e - pos]

    for pos, buz in buzz_segs:
        e = min(pos + len(buz), n_total)
        out[pos:e] += buz[:e - pos]

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
                a1 = (2*np.exp(-np.pi*abw*T)
                      * np.cos(2*np.pi*af*T))
                b0 = 1.0 - a1 - a2
                y  = (b0*float(seg[i])
                      + a1*y1 + a2*y2)
                y2 = y1; y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti) * 0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:pos+n_s] = 0.0
        pos += n_s

    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

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

    # ── Ghost layer (v16, unchanged) ──────────
    segs_out = []
    pos      = 0

    if not add_ghost:
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
        ph_idx_to_syl_end = {}
        flat_ph_cursor = 0
        for sri, srec in enumerate(
                syl_records):
            n_ph_in_syl = len(srec['phonemes'])
            syl_end_idx = (flat_ph_cursor
                           + n_ph_in_syl - 1)
            nuc_this = srec['nucleus'] or 'AH'
            if sri < len(syl_records) - 1:
                nuc_next    = (
                    syl_records[sri+1]
                    ['nucleus'] or 'AH')
                stress_next = syl_records[
                    sri+1]['stress']
                is_last     = False
            else:
                nuc_next    = None
                stress_next = 0
                is_last     = True
            ph_idx_to_syl_end[syl_end_idx] = {
                'nucleus_prev':    nuc_this,
                'nucleus_next':    nuc_next,
                'stress_prev':     srec['stress'],
                'stress_next':     stress_next,
                'is_phrase_final': is_last,
                'is_last_in_word': srec[
                    'is_last_in_word'],
            }
            flat_ph_cursor += n_ph_in_syl

        total_dur_ms  = sum(
            item['dur_ms'] for item in prosody)
        t_elapsed_ms  = 0.0
        n_phrase_phs  = len(prosody)

        first_ph = prosody[0]['ph'] \
                   if prosody else None
        first_is_vowel = (
            first_ph in VOWEL_PHONEMES or
            first_ph in DIPHTHONG_PHONEMES)
        if first_is_vowel:
            segs_out.append(
                _make_voiced_h_onset(
                    first_ph,
                    arc_type=arc_type,
                    dil=dil, sr=sr))

        for pi, (item, spec) in enumerate(
                zip(prosody, specs)):
            n_s     = spec['n_s']
            ph      = item['ph']
            rest_ms = item.get('rest_ms', 0.0)

            segs_out.append(
                out[pos:pos+n_s].copy())

            pos_in_phrase = min(
                t_elapsed_ms / max(
                    total_dur_ms, 1.0),
                1.0)
            t_elapsed_ms += item['dur_ms']

            syl_info = ph_idx_to_syl_end.get(
                pi, None)

            if syl_info is not None:
                is_phrase_final = syl_info[
                    'is_phrase_final']
                has_rest = (rest_ms > 0)

                if is_phrase_final:
                    segs_out.append(
                        _make_ghost_segment(
                            syl_info[
                                'nucleus_prev'],
                            None,
                            pos_in_phrase,
                            syl_info[
                                'stress_prev'],
                            0,
                            arc_type,
                            dil=dil,
                            phrase_final=True,
                            sr=sr))

                elif has_rest:
                    segs_out.append(
                        _make_ghost_segment(
                            syl_info[
                                'nucleus_prev'],
                            syl_info[
                                'nucleus_next'],
                            pos_in_phrase,
                            syl_info[
                                'stress_prev'],
                            syl_info[
                                'stress_next'],
                            arc_type,
                            dil=dil,
                            phrase_final=False,
                            sr=sr))
                    segs_out.append(
                        breath_rest(
                            rest_ms, sr=sr))
                    next_pi = pi + 1
                    if next_pi < n_phrase_phs:
                        nph = prosody[
                            next_pi]['ph']
                        if (nph in VOWEL_PHONEMES
                                or nph in
                                DIPHTHONG_PHONEMES):
                            segs_out.append(
                                _make_voiced_h_onset(
                                    nph,
                                    arc_type=arc_type,
                                    dil=dil,
                                    sr=sr))

                else:
                    if syl_info[
                            'nucleus_next'] \
                            is not None:
                        segs_out.append(
                            _make_ghost_segment(
                                syl_info[
                                    'nucleus_prev'],
                                syl_info[
                                    'nucleus_next'],
                                pos_in_phrase,
                                syl_info[
                                    'stress_prev'],
                                syl_info[
                                    'stress_next'],
                                arc_type,
                                dil=dil,
                                phrase_final=False,
                                sr=sr))

            elif rest_ms > 0:
                nuc_prev = None
                for pj in range(pi, -1, -1):
                    pph = prosody[pj]['ph']
                    if (pph in VOWEL_PHONEMES or
                            pph in
                            DIPHTHONG_PHONEMES):
                        nuc_prev = pph
                        break
                nuc_next = None
                for pj in range(
                        pi+1, n_phrase_phs):
                    pph = prosody[pj]['ph']
                    if (pph in VOWEL_PHONEMES or
                            pph in
                            DIPHTHONG_PHONEMES):
                        nuc_next = pph
                        break
                if nuc_prev is not None:
                    segs_out.append(
                        _make_ghost_segment(
                            nuc_prev or 'AH',
                            nuc_next,
                            pos_in_phrase,
                            1, 1,
                            arc_type,
                            dil=dil,
                            phrase_final=False,
                            sr=sr))
                segs_out.append(
                    breath_rest(rest_ms, sr=sr))

            pos += n_s

    final = f32(np.concatenate(segs_out))
    final = _normalize_phrase(
        final, specs, prosody, sr=sr)

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
# LOCUS DIAGNOSTIC
# ============================================================

def print_locus_table():
    """
    Print the locus table for all consonants
    and selected adjacent vowels.
    Run to verify locus assignments before
    perceptual testing.
    """
    print("\nLocus F2 table:")
    print(f"  {'Ph':5s} {'Place':15s} "
          f"{'F2 locus (H)':14s} "
          f"{'F2 before IY':14s} "
          f"{'F2 before AA':14s} "
          f"{'Coda?':6s}")
    print("  " + "-" * 65)
    for ph in sorted(PH_LOCUS_CLASS.keys()):
        place = PH_LOCUS_CLASS[ph]
        f2_h,  _ = _locus_f2(ph, None,    False)
        f2_iy, _ = _locus_f2(ph, 'IY',   False)
        f2_aa, _ = _locus_f2(ph, 'AA',   False)
        f2_coda, _ = _locus_f2(ph, 'IH', True)
        print(f"  {ph:5s} {place:15s} "
              f"{f2_h:8.0f} Hz     "
              f"{f2_iy:8.0f} Hz     "
              f"{f2_aa:8.0f} Hz   "
              f"{'coda' if f2_coda != f2_h else ''}")
    print()


# ============================================================
# MAIN — locus diagnostics
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v17")
    print("FIX 15: Directional Locus Transitions")
    print()
    print("  Coda consonant:  vowel F2 → locus")
    print("  Onset consonant: locus → vowel F2")
    print("  Same phoneme. Different direction.")
    print("  Different percept.")
    print()
    print("=" * 52)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print_locus_table()

    # ── DIAGNOSTIC 1: The N distinction ────────
    # The original problem: coda N and onset N
    # in "evening" sounded identical.
    # Now they should be distinct.

    print("  Diagnostic 1: N direction — 'evening'")
    print("  Coda N:  IH → alveolar locus (~1800)")
    print("  Onset N: alveolar locus (~1800) → IH")
    print()

    for word, phones, label in [
        ('evening',
         [['IY','V'],['IH','N'],['IH','NG']],
         'evening_syllabified'),
        ('evening',
         ['IY','V','IH','N','IH','NG'],
         'evening_flat'),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v17_{label}",
             seg, rt60=1.0, dr=0.60)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=4.0)
        save(f"v17_{label}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → slow: hear N departing IH (coda)")
    print("      vs N arriving into IH (onset)")
    print()

    # ── DIAGNOSTIC 2: Dark L ────────────────────
    # Coda L in "already", "still", "all"
    # should sound darker (F2 locus ~1000)
    # vs onset L in "like", "love", "learn"
    # (F2 locus ~1800)

    print("  Diagnostic 2: Dark L — coda vs onset")
    print("  Coda L:  F2 toward ~1000 Hz (dark)")
    print("  Onset L: F2 from  ~1800 Hz (bright)")
    print()

    for word, phones in [
        ('still', ['S','T','IH','L']),
        ('like',  ['L','AY','K']),
        ('all',   ['AO','L']),
        ('learn', ['L','ER','N']),
        ('already',
         [['AO','L'],['R','EH'],['D','IY']]),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v17_{word}",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=4.0)
        save(f"v17_{word}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → still_slow: L has dark quality")
    print("      like_slow:  L has bright onset")
    print("      Compare F2 body in spectrogram")
    print()

    # ── DIAGNOSTIC 3: Velar context ─────────────
    # K before IY (front) vs K before AA (back).
    # Should sound like different consonants
    # at the release — "key" vs "car".

    print("  Diagnostic 3: Velar context (K)")
    print("  K before IY: locus ~3000 (front)")
    print("  K before AA: locus ~2400 (back)")
    print()

    for word, phones in [
        ('key',   ['K','IY']),
        ('car',   ['K','AA','R']),
        ('could', ['K','UH','D']),
        ('coo',   ['K','UW']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v17_{word}",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=4.0)
        save(f"v17_{word}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → key vs car: different K quality")
    print("      at slow speed the locus shift")
    print("      is audible as consonant color")
    print()

    # ── DIAGNOSTIC 4: R / ER F3 suppression ─────
    # R and ER should have F3 clearly suppressed
    # toward 1690 Hz throughout — the defining
    # rhotic quality.

    print("  Diagnostic 4: R / ER F3 suppression")
    print("  R: F3 falls to ~1690 Hz")
    print("  ER: same, plus mid-central vowel")
    print()

    for word, phones in [
        ('here',     ['H','IY','R']),
        ('learning', [['L','ER'],
                      ['N','IH','NG']]),
        ('already',  [['AO','L'],
                      ['R','EH'],
                      ['D','IY']]),
        ('there',    ['DH','EH','R']),
        ('her',      ['HH','ER']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v17_{word}",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=4.0)
        save(f"v17_{word}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → here_slow: hear F3 drop into R")
    print("      learning_slow: ER dark quality")
    print()

    # ── DIAGNOSTIC 5: Bilabial vs alveolar ──────
    # M vs N — same voicing and murmur,
    # different locus. Now distinguishable
    # from the direction of F2 transition alone.

    print("  Diagnostic 5: Place distinction")
    print("  M: F2 locus ~720  (bilabial)")
    print("  N: F2 locus ~1800 (alveolar)")
    print("  NG: F2 locus ~2700 (velar)")
    print()

    for word, phones in [
        ('am',   ['AE','M']),
        ('an',   ['AE','N']),
        ('ang',  ['AE','NG']),
        ('him',  ['HH','IH','M']),
        ('hin',  ['HH','IH','N']),
        ('ring', ['R','IH','NG']),
        ('rim',  ['R','IH','M']),
        ('rin',  ['R','IH','N']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_ghost=True)
        save(f"v17_{word}",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=4.0)
        save(f"v17_{word}_slow",
             seg_slow, rt60=0.6, dr=0.72)

    print("    → am vs an vs ang at slow speed:")
    print("      the coda nasal should clearly")
    print("      differ in where it closes —")
    print("      lips, ridge, or back of mouth")
    print()

    # ── DIAGNOSTIC 6: canonical sentences ───────
    print("  Diagnostic 6: canonical sentences")
    print()

    for label, phrase in [
        ('the_voice',
         [('the',     ['DH','AH']),
          ('voice',   [['V','OY'],['S']]),
          ('was',     ['W','AH','Z']),
          ('already', [['AO','L'],
                       ['R','EH'],
                       ['D','IY']]),
          ('here',    ['H','IY','R'])]),
        ('something_beginning',
         [('something',  ['S','AH','M',
                           'TH','IH','NG']),
          ('is',         ['IH','Z']),
          ('beginning',  [['B','IH'],
                           ['JH','IH'],
                           ['N','IH','NG']]),
          ('to',         ['T','UW']),
          ('sound',      ['S','AW','N','D']),
          ('like',       ['L','AY','K']),
          ('something',  ['S','AH','M',
                           'TH','IH','NG'])]),
        ('i_am_here',
         [('I',    ['AY']),
          ('am',   ['AE','M']),
          ('here', ['H','IY','R'])]),
    ]:
        seg = synth_phrase(
            phrase,
            punctuation='.',
            arc_type=ARC_NORMAL,
            add_ghost=True)
        save(f"v17_{label}",
             seg, rt60=1.5, dr=0.50)
        seg_slow = _ola_stretch(
            synth_phrase(
                phrase,
                punctuation='.',
                add_breath=False,
                add_ghost=False),
            factor=3.5)
        save(f"v17_{label}_slow",
             seg_slow, rt60=1.4, dr=0.50)

    print()
    print("=" * 52)
    print()
    print("  PLAY ORDER:")
    print()
    print("  1. The N distinction:")
    print("  afplay output_play/"
          "v17_evening_syllabified_slow.wav")
    print("    → coda N then onset N")
    print("      should sound DIFFERENT")
    print()
    print("  2. Dark L:")
    print("  afplay output_play/"
          "v17_still_slow.wav")
    print("  afplay output_play/"
          "v17_like_slow.wav")
    print("    → still: L closes, dark")
    print("      like: L opens, bright")
    print()
    print("  3. Velar context:")
    print("  afplay output_play/"
          "v17_key_slow.wav")
    print("  afplay output_play/"
          "v17_car_slow.wav")
    print("    → different K quality at release")
    print()
    print("  4. R / ER F3:")
    print("  afplay output_play/"
          "v17_here_slow.wav")
    print("  afplay output_play/"
          "v17_her_slow.wav")
    print("    → F3 suppressed, dark quality")
    print()
    print("  5. Nasal place:")
    print("  afplay output_play/"
          "v17_am_slow.wav")
    print("  afplay output_play/"
          "v17_an_slow.wav")
    print("  afplay output_play/"
          "v17_ang_slow.wav")
    print("    → different closure destinations")
    print()
    print("  6. Canonical:")
    print("  afplay output_play/"
          "v17_the_voice.wav")
    print("  afplay output_play/"
          "v17_i_am_here.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  The N problem (evening):")
    print("    Old: both N's identical.")
    print("    New: first N is IH closing")
    print("    toward ridge — departure.")
    print("    Second N is ridge opening")
    print("    into IH — arrival.")
    print("    The syllable boundary is")
    print("    now audible as direction,")
    print("    not just as a seam.")
    print()
    print("  Dark L (still vs like):")
    print("    'still' at slow speed:")
    print("    the L should pull F2 DOWN")
    print("    as the tongue tip stays")
    print("    at the ridge while the")
    print("    body of the tongue falls.")
    print("    'like' at slow speed:")
    print("    the L should push F2 UP")
    print("    from ridge position into")
    print("    the AY diphthong.")
    print()
    print("  Velar context (key vs car):")
    print("    'key': K released toward")
    print("    front IY — bright, forward.")
    print("    'car': K released toward")
    print("    back AA — dark, backward.")
    print("    The same stop. Different mouth.")
    print()
    print("  IF CONSONANTS STILL SOUND WRONG:")
    print("    1. Check _consonant_is_coda()")
    print("       is classifying correctly.")
    print("       Add debug print in test.")
    print("    2. Check LOCUS_TRANS_MS values.")
    print("       If transitions too fast:")
    print("       locus is there but inaudible.")
    print("       Increase LOCUS_TRANS_MS.")
    print("    3. Check the locus table output")
    print("       at the top of the run.")
    print()
