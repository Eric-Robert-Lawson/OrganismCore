"""
VOICE PHYSICS v14
February 2026

FIX 12: ANTICIPATORY COARTICULATION

  REVISION 2 — "i um here" diagnosis:

  The first run of v14 was heard as
  "I um here" instead of "I am here."

  ROOT CAUSE:
    Two independent effects both collapsed
    AE toward AH (schwa):

    1. NASAL_COART_BLEND = 0.40
       Blended AE formants 40% toward
       NASAL_MURMUR_F = [250, 1000, ...].
       NASAL_MURMUR_F[0] = 250Hz is the
       nasal resonance frequency, not the
       vowel onset position.
       AE F1 = 660Hz.
       Blended: 660*0.6 + 250*0.4 = 496Hz.
       496Hz is AH (520Hz). The ear hears AH.
       That is "um", not "am."

    2. NASAL_MURMUR re-filtering in FIX 12C
       passed the tract output through
       nasal resonators at 250Hz etc,
       adding further low-frequency weight
       to the vowel tail, darkening it
       further toward AH.

    Both effects firing together = AE → AH
    = "I um here."

  THE CORRECT PHYSICS:
    Anticipatory nasalization has two
    separable acoustic effects:

    A. VELUM OPENING (the murmur):
       The velum begins to lower during
       the vowel tail. This adds a LOW-
       AMPLITUDE nasal murmur that is
       ADDITIVE to the oral vowel signal.
       It does NOT replace the oral vowel
       formants. F1/F2 of the oral vowel
       remain largely intact until the
       full nasal closure occurs.
       The dominant percept is still the
       oral vowel with a slight nasal
       quality added.

    B. FORMANT MODIFICATION:
       Oral cavity formants do shift
       slightly toward the nasal
       configuration — but the shift is
       SMALL in the vowel body and only
       becomes large at the very end of
       the vowel (at the M closure itself).
       For AE before M:
         F1 moves slightly toward 550Hz
         (not toward 250Hz — that is the
         nasal resonance, not the
         approaching closure position).
         F2 moves slightly toward 1500Hz
         (lips beginning to close).
       The shift is ~15% at most during
       the vowel body.

  THE FIXES:

    FIX 12B CORRECTION:
      NASAL_COART_BLEND: 0.40 → 0.18
      NASAL_MURMUR_F target for F_end
      blend replaced with CLOSURE_F:
        M closure: F1 → 550, F2 → 900
          (lips closing — not nasal
           resonance, but bilabial
           closure approach)
        N closure: F1 → 500, F2 → 1200
          (alveolar approach)
        NG closure: F1 → 480, F2 → 1000
          (velar approach)
      These are where the vowel tract
      is HEADING, not where the nasal
      tract resonates.

    FIX 12C CORRECTION:
      NASAL_ANTICIPATION_GAIN: 0.12 → 0.07
      Murmur is additive but subtle.
      It should add nasality without
      darkening the vowel.
      The murmur filter still uses
      NASAL_MURMUR_F (correct — that is
      the nasal tract resonance), but
      its gain is low enough that it
      colors without replacing.

    FIX 12A CORRECTION:
      COART_DUR_COMPRESS: 0.82 → 0.88
      Less duration loss.
      The clean vowel is audible
      for longer before the tail begins
      its transition.
      The "um" percept was partly caused
      by the vowel being too short to
      establish its identity before
      the compressed tail dominated.

  All other v13 fixes unchanged.

BUG FIXED (v14 rev1):
  get_b(ph, i) → TypeError.
  Fixed to get_b(ph)[i] pattern.
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
from scipy.signal import lfilter
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v14'


# ============================================================
# FIX 12 CONSTANTS — REVISED
# ============================================================

# All phonemes that cause anticipatory
# coarticulation in a preceding vowel.
CLOSING_PHS = {
    'M', 'N', 'NG',          # nasal closures
    'B', 'D', 'G', 'P', 'T', 'K',  # stops
    'L',                      # lateral
}

NASAL_CLOSING_PHS = {'M', 'N', 'NG'}
STOP_CLOSING_PHS  = {
    'B', 'D', 'G', 'P', 'T', 'K'}

# ── FIX 12A ──────────────────────────────
# Vowel duration compression factor.
# REVISED: 0.82 → 0.88
# Less compression = cleaner vowel body
# = AE is recognisably AE before tail.
COART_DUR_COMPRESS = 0.88

# ── FIX 12C ──────────────────────────────
# Nasal murmur additive gain.
# REVISED: 0.12 → 0.07
# Low enough to add nasal color
# without darkening the vowel body.
NASAL_ANTICIPATION_GAIN = 0.07

# Duration of nasal anticipation zone (ms).
NASAL_ANTICIPATION_MS   = 28.0

# Nasal tract resonance — used for the
# ADDITIVE murmur in FIX 12C only.
# NOT used as F_end blend target
# (that caused the AE → AH collapse).
NASAL_MURMUR_F = [250.0, 1000.0,
                   2200.0, 3300.0]
NASAL_MURMUR_B = [ 80.0,  150.0,
                    200.0,  250.0]

# ── FIX 12B ──────────────────────────────
# CLOSURE APPROACH TARGETS
# These are where the oral tract is
# HEADING as the articulator closes,
# NOT the nasal resonance frequencies.
# The vowel tract moves toward these
# as the closure forms.
#
#   M (bilabial): lips approaching closure
#     F1 drops slightly (lip closure
#     raises jaw slightly)
#     F2 drops toward ~900 (lips rounding)
#   N (alveolar): tongue tip rising
#     F1 drops slightly
#     F2 moves toward ~1200
#   NG (velar): tongue back rising
#     F1 drops slightly
#     F2 moves toward ~1000
NASAL_CLOSURE_APPROACH = {
    'M':  [550,  900, 2200, 3300],
    'N':  [500, 1200, 2200, 3300],
    'NG': [480, 1000, 2200, 3300],
}
NASAL_CLOSURE_APPROACH_B = {
    'M':  [100, 150, 220, 320],
    'N':  [100, 150, 220, 320],
    'NG': [100, 150, 220, 320],
}

# Blend toward nasal closure approach.
# REVISED: 0.40 → 0.18
# Small shift — the vowel identity is
# maintained until the closure itself.
NASAL_COART_BLEND = 0.18

# Stop closure approach: neutral.
# REVISED: 0.25 → 0.15
# Stops compress the tract slightly
# but the vowel identity is maintained.
STOP_COART_BLEND  = 0.15

# Lateral F2 target and blend.
L_COART_F2_TARGET = 1000.0
L_COART_BLEND     = 0.22


# ============================================================
# FIX 12A: VOWEL DURATION COMPRESSION
# ============================================================

def _coart_compress_dur(dur_ms, ph,
                         next_ph):
    """
    Compress vowel duration before closing
    consonant. Only for vowels/diphthongs.
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
    vowel preceding a closing consonant.

    CRITICAL DISTINCTION:
      For nasals: blend toward
        NASAL_CLOSURE_APPROACH[next_ph],
        NOT toward NASAL_MURMUR_F.
        NASAL_MURMUR_F is the nasal
        tract resonance (F1=250Hz).
        NASAL_CLOSURE_APPROACH is where
        the ORAL TRACT is heading.
        These are different.

      For stops: blend toward NEUTRAL_F
        with small factor.

      For L: lower F2 toward ~1000Hz.
    """
    if next_ph not in CLOSING_PHS:
        return None, None
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return None, None

    n_f = len(current_f)

    if next_ph in NASAL_CLOSING_PHS:
        blend     = NASAL_COART_BLEND
        tgt_f     = NASAL_CLOSURE_APPROACH.get(
            next_ph,
            NASAL_CLOSURE_APPROACH['N'])
        tgt_b     = NASAL_CLOSURE_APPROACH_B.get(
            next_ph,
            NASAL_CLOSURE_APPROACH_B['N'])
        f_end = []
        b_end = []
        for i in range(n_f):
            tf = tgt_f[i] \
                 if i < len(tgt_f) \
                 else current_f[i]
            tb = tgt_b[i] \
                 if i < len(tgt_b) \
                 else current_b[i]
            f_end.append(
                current_f[i] * (1 - blend)
                + tf * blend)
            b_end.append(
                current_b[i] * (1 - blend)
                + tb * blend)
        return f_end, b_end

    if next_ph in STOP_CLOSING_PHS:
        blend = STOP_COART_BLEND
        n_nf  = len(NEUTRAL_F)
        n_nb  = len(NEUTRAL_B)
        f_end = [
            current_f[i] * (1 - blend) +
            NEUTRAL_F[i] * blend
            if i < n_nf else current_f[i]
            for i in range(n_f)]
        b_end = [
            current_b[i] * (1 - blend) +
            NEUTRAL_B[i] * blend
            if i < n_nb else current_b[i]
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
    FIX 12B: F_end modified for vowels
    before closing consonants.
    Delegates to v13 _build_trajectories.
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

            # get_b(ph) returns a list.
            # Do NOT pass index to get_b.
            current_f = list(
                s.get('F_tgt', get_f(ph)))
            raw_b = get_b(ph)
            if isinstance(raw_b,
                          (list, tuple)):
                default_b = list(raw_b)
            else:
                default_b = [float(raw_b)] * 4
            current_b = list(
                s.get('B_tgt', default_b))

            f_end, b_end = _coart_f_end(
                ph, next_ph,
                current_f, current_b)
            if f_end is not None:
                s['F_end'] = f_end
                s['B_end'] = b_end

        patched.append(s)

    return _build_trajectories(
        patched, sr=sr)


# ============================================================
# FIX 12C: NASAL MURMUR ONSET (REVISED)
# Low gain additive murmur.
# Does NOT alter F_tgt.
# Does NOT blend toward nasal resonance.
# Adds nasal COLOR to the vowel tail.
# ============================================================

def _apply_nasal_anticipation(
        out, specs, sr=SR):
    """
    FIX 12C: For vowels before M/N/NG,
    blend a low-gain nasal murmur into
    the final NASAL_ANTICIPATION_MS of
    the vowel body.

    The murmur is the existing output
    re-filtered through nasal resonators,
    then added at NASAL_ANTICIPATION_GAIN.
    The oral vowel signal is unchanged.
    The murmur is purely additive.

    NASAL_ANTICIPATION_GAIN = 0.07 means
    the murmur is 7% the peak amplitude
    of the existing signal in that zone.
    Audible as nasal coloring, not as
    a formant shift.
    """
    n_total = len(out)
    n_ant   = int(
        NASAL_ANTICIPATION_MS / 1000.0 * sr)
    n_specs = len(specs)
    T       = 1.0 / sr

    pos = 0
    for si, spec in enumerate(specs):
        n_s     = spec['n_s']
        ph      = spec['ph']
        next_ph = (specs[si + 1]['ph']
                   if si < n_specs - 1
                   else None)
        is_v    = (ph in VOWEL_PHONEMES or
                   ph in DIPHTHONG_PHONEMES)

        if next_ph in NASAL_CLOSING_PHS \
                and is_v:
            n_off = min(trans_n(ph, sr),
                        n_s // 3)
            n_on  = min(trans_n(ph, sr),
                        n_s // 3)

            vowel_end    = pos + n_s - n_off
            murmur_start = max(
                pos + n_on,
                vowel_end - n_ant)
            murmur_end   = min(
                vowel_end, n_total)
            n_m = murmur_end - murmur_start

            if n_m < 4:
                pos += n_s
                continue

            src    = np.array(
                out[murmur_start:murmur_end],
                dtype=np.float64)
            murmur = np.zeros(
                n_m, dtype=np.float64)

            for fc, bw in zip(
                    NASAL_MURMUR_F,
                    NASAL_MURMUR_B):
                pole_r = np.exp(
                    -np.pi * bw * T)
                cos_t  = np.cos(
                    2.0 * np.pi * fc * T)
                a1 =  2.0 * pole_r * cos_t
                a2 = -(pole_r ** 2)
                b0 = 1.0 - a1 - a2
                stage = lfilter(
                    [b0], [1.0, -a1, -a2],
                    src)
                murmur += stage

            peak = np.max(np.abs(murmur))
            if peak > 1e-8:
                murmur = (murmur / peak *
                    NASAL_ANTICIPATION_GAIN)

            env = np.linspace(
                0.0, 1.0, n_m)
            out[murmur_start:murmur_end] \
                = f32(
                    out[murmur_start:
                        murmur_end].astype(
                        np.float64)
                    + murmur * env)

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
    All three FIX 12 components active
    with revised parameters.
    All v13 fixes preserved.
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

    prosody = plan_prosody(
        flat_words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch_base,
        dil=dil)

    if not prosody:
        return f32(np.zeros(
            int(0.1 * sr)))

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
        word_      = item.get('word', '')
        next_ph    = (prosody[i + 1]['ph']
                      if i < n_items - 1
                      else None)

        # Word-final fricative cap (v13).
        FRICS = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH'}
        if word_final and ph in FRICS:
            dur_ms = min(
                dur_ms, FINAL_FRIC_MAX_MS)

        # Per-word emphasis (v13 FIX 11).
        if word_ in word_emphasis:
            emph    = word_emphasis[word_]
            pitch_ *= float(
                emph.get('f0_boost', 1.0))
            dur_ms *= float(
                emph.get('dur_mult',  1.0))
            amp_   *= float(
                emph.get('amp_boost', 1.0))

        # FIX 12A: compress vowel before
        # closing consonant.
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

    # FIX 12B: trajectories with
    # closure approach F_end.
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

    # Nasal antiformants — unchanged
    # from v9–v13.
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
            seg  = out[pos:pos + n_s].copy()
            anti = np.zeros(n_s, dtype=DTYPE)
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

    # FIX 12C: additive nasal murmur
    # in vowel tail before M/N/NG.
    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

    # Amplitude envelope (v13 FIX 10).
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos + n_s] *= item['amp']
        pos += n_s

    # Edge envelope (v13 FIX 10).
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
            out[pos:pos + n_s].copy())
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
# CONVENIENCE WRAPPERS
# ============================================================

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
# MAIN — self test
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v14 — rev2")
    print("'i am here' fix")
    print()
    print("  REVISED PARAMETERS:")
    print(f"  COART_DUR_COMPRESS:     "
          f"{COART_DUR_COMPRESS}  (was 0.82)")
    print(f"  NASAL_COART_BLEND:      "
          f"{NASAL_COART_BLEND}  (was 0.40)")
    print(f"  NASAL_ANTICIPATION_GAIN:"
          f" {NASAL_ANTICIPATION_GAIN}  (was 0.12)")
    print()
    print("  F_end target for nasals:")
    print("  M → bilabial approach "
          "[550, 900, 2200, 3300]")
    print("  N → alveolar approach "
          "[500, 1200, 2200, 3300]")
    print("  NG→ velar approach    "
          "[480, 1000, 2200, 3300]")
    print("  NOT nasal resonance   "
          "[250, 1000, ...]")
    print()
    print("=" * 52)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Primary: 'I am here'")
    seg = synth_phrase(
        [('I',    ['AY']),
         ('am',   ['AE', 'M']),
         ('here', ['H',  'IY', 'R'])],
        punctuation='.',
        pitch_base=PITCH,
        arc_type=ARC_NORMAL)
    save("v14r2_i_am_here",
         seg, rt60=1.4, dr=0.52)

    print()
    print("  'I am here' slow 3.5×")
    import numpy as np as _np

    def _ola(sig, factor, win_ms=25,
              sr=SR):
        sig   = _np.array(
            sig, dtype=_np.float64)
        n_in  = len(sig)
        win_n = int(win_ms / 1000.0 * sr)
        if win_n % 2 != 0:
            win_n += 1
        hop_in  = win_n // 4
        hop_out = int(hop_in * factor)
        if hop_out == 0:
            hop_out = 1
        n_frames = max(1,
            (n_in - win_n) // hop_in + 1)
        n_out = (hop_out * (n_frames - 1)
                 + win_n)
        out  = _np.zeros(
            n_out, dtype=_np.float64)
        norm = _np.zeros(
            n_out, dtype=_np.float64)
        window = _np.hanning(win_n)
        for i in range(n_frames):
            i0 = i * hop_in
            i1 = i0 + win_n
            if i1 > n_in:
                frame = _np.zeros(win_n)
                av = n_in - i0
                if av > 0:
                    frame[:av] = sig[
                        i0:i0 + av]
            else:
                frame = sig[i0:i1]
            o0 = i * hop_out
            o1 = o0 + win_n
            out[o0:o1]  += frame * window
            norm[o0:o1] += window
        norm = _np.where(
            norm < 1e-8, 1.0, norm)
        return f32(out / norm)

    seg2 = synth_phrase(
        [('I',    ['AY']),
         ('am',   ['AE', 'M']),
         ('here', ['H',  'IY', 'R'])],
        punctuation='.',
        pitch_base=PITCH,
        add_breath=False)
    seg2 = _ola(seg2, factor=3.5)
    save("v14r2_i_am_here_slow",
         seg2, rt60=1.4, dr=0.52)

    print()
    print("  Nasal isolation: am / him / sun")
    for word, phones in [
        ('am',   ['AE', 'M']),
        ('him',  ['HH', 'IH', 'M']),
        ('sun',  ['S',  'AH', 'N']),
        ('ring', ['R',  'IH', 'NG']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_breath=False)
        save(f"v14r2_{word}",
             seg, rt60=0.8, dr=0.65)

        seg_s = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_breath=False)
        seg_s = _ola(seg_s, factor=4.0)
        save(f"v14r2_{word}_slow",
             seg_s, rt60=0.6, dr=0.72)

    print()
    print("  Baseline: the voice was"
          " already here")
    seg = synth_phrase(
        [('the',     ['DH', 'AH']),
         ('voice',   ['V',  'OY', 'S']),
         ('was',     ['W',  'AH', 'Z']),
         ('already', ['AA', 'L',  'R',
                       'EH', 'D', 'IY']),
         ('here',    ['H',  'IY', 'R'])],
        punctuation='.',
        arc_type=ARC_NORMAL)
    save("v14r2_the_voice_was_already_here",
         seg, rt60=1.5, dr=0.50)

    print()
    print("  PLAY:")
    print("  afplay output_play/"
          "v14r2_i_am_here.wav")
    print("  afplay output_play/"
          "v14r2_i_am_here_slow.wav")
    print("  afplay output_play/"
          "v14r2_am_slow.wav")
    print()
    print("  IF STILL HEARING 'um':")
    print("  Lower NASAL_COART_BLEND")
    print("    current:", NASAL_COART_BLEND,
          "→ try 0.10")
    print("  Lower NASAL_ANTICIPATION_GAIN")
    print("    current:",
          NASAL_ANTICIPATION_GAIN,
          "→ try 0.04")
    print()
    print("  IF NASAL QUALITY IS GONE:")
    print("  Raise NASAL_ANTICIPATION_GAIN")
    print("    current:",
          NASAL_ANTICIPATION_GAIN,
          "→ try 0.10")
    print()
