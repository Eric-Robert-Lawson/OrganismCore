"""
VOICE PHYSICS v15
February 2026

FIX 13: AFFRICATES — JH and CH

  JH = /dʒ/ — voiced palatal affricate
    "judge", "gin", "begin", "age",
    "general", "ginger"

  CH = /tʃ/ — unvoiced palatal affricate
    "church", "nature", "beach",
    "which", "each", "much"

  ROOT CAUSE OF MISSING AFFRICATES:
    v13 already listed CH and JH in
    H_STOP_PHS (for H-bypass decisions)
    but provided no source handler and
    no ph_spec entry. Both fell through
    silently to stop_voiced / stop_unvoiced
    physics, producing a plain stop burst
    with no frication release.

    The perceptual result: "be-gin-ing"
    sounds like "be-GOIN-ing" — a velar
    stop where the ear expects an affricate.

  WHAT AN AFFRICATE IS:
    A stop closure followed immediately
    by a fricative release at the same
    place of articulation.
    The burst IS the frication onset —
    there is no gap between them.

    JH: voiced palatal
      Closure: brief voiced murmur (~28ms)
               like a short voiced stop
      Release: ZH-like frication (~55ms)
               broadband noise 1500-7000Hz
               with voicing underneath
      Formants: palatal position (like Y)
        F1: ~250Hz  F2: ~2100Hz  F3: ~3000Hz

    CH: unvoiced palatal
      Closure: silence (~30ms)
               like a short unvoiced stop
      Release: SH-like frication (~55ms)
               broadband noise 1800-8000Hz
               no voicing
      Formants: palatal position
        F1: ~250Hz  F2: ~2100Hz  F3: ~3000Hz

  THE SOFT G / HARD G RULE:
    English letter G before E, I, Y → JH
    English letter G before A, O, U → G
    This is the "soft G / hard G" rule.

    begin    → B IH JH IH N         (soft G)
    garden   → G AA R D AH N        (hard G)
    gin      → JH IH N              (soft G)
    ginger   → JH IH N JH ER        (soft G)
    go       → G OW                 (hard G)
    age      → EY JH                (soft G)
    large    → L AA R JH            (soft G)

  IMPLEMENTATION:
    New source type: 'affricate_voiced'
      Used for JH.
      Closure: voiced murmur × 0.04
      Release: ZH bypass added to
               bypass_segs (through tract)
               + voiced buzz underneath

    New source type: 'affricate_unvoiced'
      Used for CH.
      Closure: silence
      Release: SH bypass added to
               bypass_segs

    ph_spec_v15() wraps ph_spec_v9()
    and adds JH and CH to the STYPE
    and STOP tables.

    VOWEL_F: JH and CH palatal targets
    added so get_f() returns correct
    tract position for the release phase.

    PHON_DUR_BASE: JH=85ms, CH=90ms
    These propagate to v3's table via
    the existing import chain.

  All v14 fixes preserved unchanged.

  Import chain:
    v15 → v14 → v13 → v9 → v8 → ... → v3
"""

from voice_physics_v14 import (
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
    synth_phrase as _synth_phrase_v14,
    save as _save_v14,
)

import numpy as np
from scipy.signal import lfilter
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v15'


# ============================================================
# FIX 13: AFFRICATE CONSTANTS
# ============================================================

# Palatal formant targets.
# Both JH and CH use palatal tract position —
# high front, similar to Y approximant.
# Distinguish from velar G/K (which is more back).
JH_F = [250, 2100, 3000, 3700]
JH_B = [ 80,  120,  200,  280]
CH_F = [250, 2100, 3000, 3700]
CH_B = [ 80,  120,  200,  280]

# Phase split: fraction of total duration
# spent in closure vs frication release.
# Affricates are ~30% closure, 70% release.
AFFRICATE_CLOSURE_FRAC = 0.30
AFFRICATE_FRIC_FRAC    = 0.70

# JH release: ZH-like voiced frication
JH_FRIC_LO         = 1500   # Hz bandpass lo
JH_FRIC_HI         = 7000   # Hz bandpass hi
JH_CLOSURE_AMP     = 0.04   # voiced murmur amp
JH_FRIC_NOISE_AMP  = 0.55   # noise in release
JH_FRIC_VOICED_AMP = 0.40   # voicing in release
JH_BUZZ_GAIN       = 0.25   # buzz_seg gain

# CH release: SH-like unvoiced frication
CH_FRIC_LO         = 1800   # Hz bandpass lo
CH_FRIC_HI         = 8000   # Hz bandpass hi
CH_FRIC_NOISE_AMP  = 0.72   # noise in release

# Duration caps
JH_MAX_MS = 120
CH_MAX_MS = 125

# Coarticulation fraction — abrupt
JH_CF = 0.12
CH_CF = 0.12

# PHON_DUR_BASE additions.
# These supplement v3's PHON_DUR_BASE
# for phonemes not yet in that table.
AFFRICATE_DUR_BASE = {
    'JH': 85,
    'CH': 90,
}

# APPROX_MAX_MS additions for affricates
AFFRICATE_MAX_MS = {
    'JH': JH_MAX_MS,
    'CH': CH_MAX_MS,
}

# get_f / get_b entries for JH and CH.
# These are used by ph_spec and trajectory
# builder to set tract position.
AFFRICATE_F = {
    'JH': JH_F,
    'CH': CH_F,
}
AFFRICATE_B = {
    'JH': JH_B,
    'CH': CH_B,
}


# ============================================================
# PATCHED get_f / get_b
# Adds JH and CH to formant lookup.
# ============================================================

def get_f_v15(phon):
    """get_f with JH and CH added."""
    if phon in AFFRICATE_F:
        return AFFRICATE_F[phon]
    return get_f(phon)

def get_b_v15(phon):
    """get_b with JH and CH added."""
    if phon in AFFRICATE_B:
        return AFFRICATE_B[phon]
    return get_b(phon)


# ============================================================
# PATCHED plan_prosody
# Adds JH and CH duration caps.
# FIX: caller's phonemes take priority
# (already fixed in v3/v9, preserved here).
# ============================================================

def plan_prosody_v15(words_phonemes,
                      punctuation='.',
                      pitch_base=PITCH,
                      dil=DIL):
    """
    v15 prosody planner.
    Adds JH_MAX_MS and CH_MAX_MS caps.
    All v9 and prior fixes preserved.
    """
    # Use inherited plan_prosody from v13
    # via the import chain, then patch
    # the duration caps for JH and CH.
    prosody = plan_prosody(
        words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch_base,
        dil=dil)

    # Apply affricate duration caps
    from voice_physics_v3 import PHON_DUR_BASE
    for item in prosody:
        ph = item['ph']
        if ph == 'JH':
            item['dur_ms'] = min(
                item['dur_ms'], JH_MAX_MS)
        elif ph == 'CH':
            item['dur_ms'] = min(
                item['dur_ms'], CH_MAX_MS)
        # Also fix base duration if
        # PHON_DUR_BASE doesn't have JH/CH
        # (v3 table predates this version)
        if ph in AFFRICATE_DUR_BASE:
            if item['dur_ms'] <= 0:
                item['dur_ms'] = (
                    AFFRICATE_DUR_BASE[ph]
                    * dil)

    return prosody


# ============================================================
# ph_spec_v15
# Adds JH and CH to the STYPE table
# and spec builder.
# ============================================================

def ph_spec_v15(ph, dur_ms,
                 pitch=PITCH, oq=0.65,
                 bw_mult=1.0, amp=1.0,
                 next_ph=None,
                 rest_ms=0.0,
                 word_final=False,
                 sr=SR):
    """
    v15 phoneme spec.
    Adds JH and CH affricate types.
    All other phonemes delegated to
    ph_spec_v9 unchanged.
    """
    if ph not in ('JH', 'CH'):
        return ph_spec_v9(
            ph, dur_ms,
            pitch=pitch, oq=oq,
            bw_mult=bw_mult, amp=amp,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)

    n_s = max(4, int(dur_ms / 1000.0 * sr))

    F = AFFRICATE_F[ph]
    B = AFFRICATE_B[ph]

    clos_n = int(n_s * AFFRICATE_CLOSURE_FRAC)
    fric_n = n_s - clos_n

    stype = ('affricate_voiced'
             if ph == 'JH'
             else 'affricate_unvoiced')

    spec = {
        'ph':         ph,
        'F_tgt':      F,
        'B_tgt':      B,
        'bw_mult':    bw_mult,
        'n_s':        n_s,
        'coart_frac': JH_CF,
        'diphthong':  False,
        'F_end':      None,
        'r_f3':       False,
        'source':     stype,
        'pitch':      pitch,
        'oq':         oq,
        'amp':        amp,
        'word_final': word_final,
        'rest_ms':    rest_ms,
        'clos_n':     clos_n,
        'fric_n':     fric_n,
    }

    return spec


# ============================================================
# AFFRICATE SOURCE BUILDER
# Called by _build_source_and_bypass_v15
# for JH and CH segments.
# ============================================================

def _make_affricate_source(
        ph, spec, s, e, n_s,
        voiced_full, noise_full,
        tract_source, bypass_segs,
        buzz_segs, sr=SR):
    """
    Build source for one affricate
    phoneme (JH or CH).

    JH — voiced palatal affricate:
      Phase 1 (clos_n): voiced murmur
      Phase 2 (fric_n): voiced fric + bypass

    CH — unvoiced palatal affricate:
      Phase 1 (clos_n): silence
      Phase 2 (fric_n): unvoiced fric bypass
    """
    clos_n = spec.get('clos_n', int(n_s * 0.30))
    fric_n = n_s - clos_n
    fric_s = s + clos_n

    if ph == 'JH':
        # ── Closure: voiced murmur ────────
        if clos_n > 0:
            tract_source[s:s+clos_n] = (
                voiced_full[s:s+clos_n]
                * JH_CLOSURE_AMP)

        # ── Release: voiced frication ─────
        if fric_n > 0:
            # Noise component
            fric_noise = noise_full[
                fric_s:fric_s+fric_n].copy()
            try:
                b, a = safe_bp(
                    JH_FRIC_LO,
                    min(JH_FRIC_HI,
                        sr * 0.47),
                    sr)
                fric_noise = f32(
                    lfilter(b, a, fric_noise))
            except Exception:
                pass
            mx = np.max(np.abs(fric_noise))
            if mx > 1e-8:
                fric_noise = fric_noise / mx

            # Voiced component
            fric_v = voiced_full[
                fric_s:fric_s+fric_n]

            # Envelope: ramp in over 5ms,
            # ramp out over 8ms
            env = np.ones(fric_n, dtype=DTYPE)
            n_atk = min(int(0.005*sr),
                        fric_n // 4)
            n_rel = min(int(0.008*sr),
                        fric_n // 4)
            if n_atk > 0:
                env[:n_atk] = np.linspace(
                    0, 1, n_atk)
            if n_rel > 0:
                env[-n_rel:] = np.linspace(
                    1, 0, n_rel)

            fric_combined = (
                fric_v * JH_FRIC_VOICED_AMP
                + fric_noise * JH_FRIC_NOISE_AMP
            ) * f32(env)

            # Tract component (through tract)
            tract_source[fric_s:
                          fric_s+fric_n] = \
                fric_combined

            # Buzz segment (bypass, voiced
            # character of the release)
            buzz_full = np.zeros(
                n_s, dtype=DTYPE)
            buzz_full[clos_n:] = (
                voiced_full[fric_s:
                             fric_s+fric_n]
                * JH_BUZZ_GAIN * f32(env))
            buzz_segs.append(
                (s, f32(buzz_full)))

    elif ph == 'CH':
        # ── Closure: silence ──────────────
        # (tract_source already zeros)

        # ── Release: unvoiced frication ───
        if fric_n > 0:
            fric_noise = noise_full[
                fric_s:fric_s+fric_n].copy()
            try:
                b, a = safe_bp(
                    CH_FRIC_LO,
                    min(CH_FRIC_HI,
                        sr * 0.47),
                    sr)
                fric_noise = f32(
                    lfilter(b, a, fric_noise))
            except Exception:
                pass
            mx = np.max(np.abs(fric_noise))
            if mx > 1e-8:
                fric_noise = fric_noise / mx

            env = np.ones(fric_n, dtype=DTYPE)
            n_atk = min(int(0.005*sr),
                        fric_n // 4)
            n_rel = min(int(0.010*sr),
                        fric_n // 4)
            if n_atk > 0:
                env[:n_atk] = np.linspace(
                    0, 1, n_atk)
            if n_rel > 0:
                env[-n_rel:] = np.linspace(
                    1, 0, n_rel)

            # Full bypass (frication is
            # not through the tract —
            # it is independent noise)
            byp_full = np.zeros(
                n_s, dtype=DTYPE)
            byp_full[clos_n:] = (
                fric_noise
                * CH_FRIC_NOISE_AMP
                * f32(env))
            bypass_segs.append(
                (s, f32(byp_full)))


# ============================================================
# PATCHED SOURCE AND BYPASS BUILDER v15
# Intercepts JH and CH before delegating
# everything else to _build_source_and_bypass.
# ============================================================

def _build_source_and_bypass_v15(
        phoneme_specs, sr=SR):
    """
    v15 source builder.
    Handles JH and CH affricates.
    All other phonemes delegated to
    v13's _build_source_and_bypass.

    Strategy: split specs into two groups.
      Affricate specs → _make_affricate_source
      All others      → _build_source_and_bypass

    To keep the voiced_full and noise_full
    arrays consistent, we build the full
    arrays first, then call the affricate
    builder with the correct slice positions.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    has_affricate = any(
        s['ph'] in ('JH', 'CH')
        for s in phoneme_specs)

    if not has_affricate:
        return _build_source_and_bypass(
            phoneme_specs, sr=sr)

    # Build voiced_full and noise_full
    # across the whole phrase — same
    # as the v13 source builder does,
    # so the affricate slices are
    # acoustically continuous with
    # surrounding voiced phonemes.
    from voice_physics_v13 import (
        _build_f0_spline,
    )

    f0_traj = _build_f0_spline(
        phoneme_specs, sr=sr
    ).astype(np.float64)

    oq_traj = np.zeros(
        n_total, dtype=np.float64)
    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s     = spec['n_s']
        oq_this = spec.get('oq', 0.65)
        oq_next = (phoneme_specs[si+1]
                   .get('oq', 0.65)
                   if si < len(phoneme_specs)-1
                   else oq_this)
        oq_traj[pos:pos+n_s] = np.linspace(
            oq_this, oq_next, n_s)
        pos += n_s

    T     = 1.0 / sr
    raw_v = np.zeros(n_total, dtype=DTYPE)
    p     = 0.0
    for i in range(n_total):
        f0  = float(f0_traj[i])
        oq_ = max(0.40, min(0.85,
                  float(oq_traj[i])))
        p  += f0 * (1 + np.random.normal(
            0, 0.005)) * T
        if p >= 1.0:
            p -= 1.0
        raw_v[i] = (
            (p/oq_)*(2-p/oq_)
            if p < oq_
            else 1-(p-oq_)/(1-oq_+1e-9))
    raw_v = f32(np.diff(
        raw_v, prepend=raw_v[0]))
    try:
        b, a  = safe_lp(20, sr)
        sh_   = f32(np.random.normal(
            0, 1, n_total))
        sh_   = f32(lfilter(b, a, sh_))
        sh_   = f32(np.clip(
            1 + 0.030*sh_, 0.4, 1.6))
        raw_v = raw_v * sh_
    except Exception:
        pass
    asp_src = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b, a    = safe_bp(400, 2200, sr)
        asp_src = f32(lfilter(b, a, asp_src))
    except Exception:
        asp_src = f32(np.zeros(n_total))
    raw_v       = raw_v + asp_src
    voiced_full = calibrate(raw_v)
    noise_full  = calibrate(
        f32(np.random.normal(0, 1, n_total)))

    # Split: non-affricate specs get
    # delegated to v13 builder.
    # Affricate specs get our new builder.
    # We need to preserve the combined
    # bypass_segs and buzz_segs lists and
    # the tract_source array.

    # First: run v13 builder on ALL specs
    # to get the base tract_source and
    # bypass/buzz lists, then OVERWRITE
    # the affricate segments with our
    # new physics.
    base_tract, base_bypass, base_buzz = \
        _build_source_and_bypass(
            phoneme_specs, sr=sr)

    # Now overwrite affricate segments
    tract_source = np.array(
        base_tract, dtype=DTYPE)
    bypass_segs  = list(base_bypass)
    buzz_segs    = list(base_buzz)

    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s = spec['n_s']
        ph  = spec['ph']
        s   = pos
        e   = pos + n_s

        if ph in ('JH', 'CH'):
            # Zero out whatever v13 put here
            tract_source[s:e] = 0.0

            # Remove any bypass/buzz segs
            # v13 generated for this region
            bypass_segs = [
                (p, b) for p, b in bypass_segs
                if not (p >= s and p < e)]
            buzz_segs = [
                (p, b) for p, b in buzz_segs
                if not (p >= s and p < e)]

            # Apply v15 affricate physics
            _make_affricate_source(
                ph, spec, s, e, n_s,
                voiced_full, noise_full,
                tract_source,
                bypass_segs, buzz_segs,
                sr=sr)

        pos += n_s

    return f32(tract_source), \
           bypass_segs, buzz_segs


# ============================================================
# PHRASE SYNTHESIS v15
# Swaps in v15 spec builder and
# source builder for JH/CH.
# All v14 coarticulation logic preserved.
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR,
                  arc_type=ARC_NORMAL,
                  add_breath=True):
    """
    v15: All fixes active.
      FIX 13: JH and CH affricates.
      All v14 fixes (coarticulation,
      F2 preservation) preserved.
    """
    word_emphasis       = {}
    flat_words_phonemes = []
    for entry in words_phonemes:
        if len(entry) == 3:
            word, phones, emph = entry
            word_emphasis[word] = emph
        else:
            word, phones = entry[:2]
        flat_words_phonemes.append(
            (word, phones))

    # Use v15 prosody planner for
    # JH/CH duration caps
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
            emph    = word_emphasis[word_]
            pitch_ *= float(
                emph.get('f0_boost', 1.0))
            dur_ms *= float(
                emph.get('dur_mult',  1.0))
            amp_   *= float(
                emph.get('amp_boost', 1.0))

        # FIX 12A: coarticulation duration
        dur_ms = _coart_compress_dur(
            dur_ms, ph, next_ph)

        # Use v15 spec builder for JH/CH,
        # v9 spec builder for everything else
        spec = ph_spec_v15(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)
        specs.append(spec)

    # FIX 12B: per-formant trajectory
    F_full, B_full, _ = \
        _build_trajectories_v14(
            specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # v15 source builder handles JH/CH
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

    # Nasal antiformants — unchanged
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
                a2 = -np.exp(
                    -2*np.pi*abw*T)
                a1 = (2*np.exp(
                    -np.pi*abw*T) *
                    np.cos(2*np.pi*af*T))
                b0 = 1.0 - a1 - a2
                y  = (b0*float(seg[i]) +
                      a1*y1 + a2*y2)
                y2 = y1
                y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:
                    pos+n_s] = 0.0
        pos += n_s

    # FIX 12C: nasal anticipation
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
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v15")
    print("FIX 13: JH and CH affricates.")
    print()
    print("  JH = /dʒ/ voiced palatal affricate")
    print("    'judge', 'gin', 'begin'")
    print("    Closure: voiced murmur x0.04")
    print("    Release: ZH-like frication")
    print()
    print("  CH = /tʃ/ unvoiced palatal affricate")
    print("    'church', 'beach', 'much'")
    print("    Closure: silence")
    print("    Release: SH-like frication")
    print()
    print("  SOFT G / HARD G RULE:")
    print("    G before E/I/Y → JH")
    print("    G before A/O/U → G")
    print("    'begin' = B IH JH IH N")
    print("    'garden' = G AA R D AH N")
    print("=" * 52)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    # ── isolation: bare affricates ─────
    print("  Isolation tests — bare affricates...")

    for word, phones, label in [
        ('judge',   ['JH', 'AH', 'JH'],
         'judge (JH AH JH)'),
        ('gin',     ['JH', 'IH', 'N'],
         'gin (JH IH N)'),
        ('church',  ['CH', 'ER', 'CH'],
         'church (CH ER CH)'),
        ('much',    ['M',  'AH', 'CH'],
         'much (M AH CH)'),
        ('each',    ['IY', 'CH'],
         'each (IY CH)'),
        ('age',     ['EY', 'JH'],
         'age (EY JH)'),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_breath=False)
        save(f"v15_{word}",
             seg, rt60=0.8, dr=0.65)
        seg_slow = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False),
            factor=4.0)
        save(f"v15_{word}_slow",
             seg_slow, rt60=0.6, dr=0.72)
        print(f"    → {label}")

    print()

    # ── the key test: beginning ────────
    print("  Key test: 'beginning'")
    print("  OLD: B IH G IH N IH NG")
    print("  NEW: B IH JH IH N IH NG")
    print()

    seg_old = synth_phrase(
        [('beginning',
          ['B', 'IH', 'G',
           'IH', 'N', 'IH', 'NG'])],
        punctuation='.',
        add_breath=False)
    save("v15_beginning_old_G",
         seg_old, rt60=1.0, dr=0.60)
    save("v15_beginning_old_G_slow",
         _ola_stretch(
             synth_phrase(
                 [('beginning',
                   ['B', 'IH', 'G',
                    'IH', 'N', 'IH', 'NG'])],
                 punctuation='.',
                 add_breath=False),
             factor=4.0),
         rt60=0.6, dr=0.72)

    seg_new = synth_phrase(
        [('beginning',
          ['B', 'IH', 'JH',
           'IH', 'N', 'IH', 'NG'])],
        punctuation='.',
        add_breath=False)
    save("v15_beginning_new_JH",
         seg_new, rt60=1.0, dr=0.60)
    save("v15_beginning_new_JH_slow",
         _ola_stretch(
             synth_phrase(
                 [('beginning',
                   ['B', 'IH', 'JH',
                    'IH', 'N', 'IH', 'NG'])],
                 punctuation='.',
                 add_breath=False),
             factor=4.0),
         rt60=0.6, dr=0.72)

    print()

    # ── the v13 canonical sentence ─────
    print("  Canonical: 'something is")
    print("    beginning to sound like")
    print("    something'")
    print("  With corrected transcription:")
    print("    'beginning' = JH, not G")
    print()

    seg = synth_phrase(
        [('something',  ['S', 'AH', 'M',
                          'TH', 'IH', 'NG']),
         ('is',         ['IH', 'Z']),
         ('beginning',  ['B',  'IH', 'JH',
                          'IH', 'N', 'IH',
                          'NG'],
          {'f0_boost': 1.15,
           'dur_mult': 1.20,
           'amp_boost': 1.10}),
         ('to',         ['T',  'UW']),
         ('sound',      ['S',  'AW', 'N', 'D']),
         ('like',       ['L',  'AY', 'K']),
         ('something',  ['S',  'AH', 'M',
                          'TH', 'IH', 'NG'])],
        punctuation='.',
        pitch_base=PITCH * 0.92,
        arc_type=ARC_CONTAIN)
    save("v15_something_beginning",
         seg, rt60=1.8, dr=0.42)
    save("v15_something_beginning_slow",
         _ola_stretch(
             synth_phrase(
                 [('something',
                   ['S', 'AH', 'M',
                    'TH', 'IH', 'NG']),
                  ('is',         ['IH', 'Z']),
                  ('beginning',
                   ['B',  'IH', 'JH',
                    'IH', 'N', 'IH', 'NG']),
                  ('to',         ['T',  'UW']),
                  ('sound',
                   ['S',  'AW', 'N', 'D']),
                  ('like',       ['L',  'AY', 'K']),
                  ('something',
                   ['S',  'AH', 'M',
                    'TH', 'IH', 'NG'])],
                 punctuation='.',
                 pitch_base=PITCH * 0.92,
                 add_breath=False),
             factor=3.0),
         rt60=2.0, dr=0.38)

    print()

    # ── the voice was already here ─────
    print("  Baseline: the voice was already here")
    seg = synth_phrase(
        [('the',     ['DH', 'AH']),
         ('voice',   ['V',  'OY', 'S']),
         ('was',     ['W',  'AH', 'Z']),
         ('already', ['AO', 'L',  'R',
                       'EH', 'D', 'IY']),
         ('here',    ['H',  'IY', 'R'])],
        punctuation='.',
        arc_type=ARC_NORMAL)
    save("v15_the_voice_was_already_here",
         seg, rt60=1.5, dr=0.50)

    print()
    print("=" * 52)
    print()
    print("  START HERE — affricate identity:")
    print("  afplay output_play/v15_judge.wav")
    print("  afplay output_play/v15_church.wav")
    print("  afplay output_play/v15_gin.wav")
    print("  afplay output_play/v15_much.wav")
    print()
    print("  KEY COMPARISON — 'beginning':")
    print("  afplay output_play/"
          "v15_beginning_old_G_slow.wav")
    print("  afplay output_play/"
          "v15_beginning_new_JH_slow.wav")
    print("  → old: stop burst, velar")
    print("  → new: stop + frication, palatal")
    print()
    print("  CANONICAL SENTENCE:")
    print("  afplay output_play/"
          "v15_something_beginning.wav")
    print("  afplay output_play/"
          "v15_something_beginning_slow.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  v15_judge.wav:")
    print("    Two JH sounds around AH.")
    print("    Should sound like 'judge'.")
    print("    Not like 'dud' or 'bud'.")
    print()
    print("  v15_church.wav:")
    print("    Two CH sounds around ER.")
    print("    Should sound like 'church'.")
    print("    Not like 'tur' or 'turt'.")
    print()
    print("  v15_beginning comparison:")
    print("    Old: hard velar stop mid-word.")
    print("    New: affricate — stop into")
    print("    frication. 'begin' not 'begoin'.")
    print()
    print("  IF JH SOUNDS LIKE A PLAIN STOP:")
    print("    The frication release is")
    print("    not reaching the output.")
    print("    Check buzz_segs and bypass_segs")
    print("    are being applied in synth_phrase.")
    print()
    print("  IF CH SOUNDS LIKE SH ONLY:")
    print("    The closure silence is too long.")
    print("    Reduce AFFRICATE_CLOSURE_FRAC.")
    print()
