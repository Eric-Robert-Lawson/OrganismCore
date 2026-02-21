"""
VOICE PHYSICS v14
February 2026

FIX 12: ANTICIPATORY COARTICULATION

  REVISION 3 — still hearing "um"

  ROOT CAUSE (rev 2 post-mortem):
    Even with NASAL_COART_BLEND = 0.18,
    the F2 shift was too large.

    AE F2 = 1720 Hz.
    M-closure approach F2 = 900 Hz.
    Blend: 1720 * 0.82 + 900 * 0.18 = 1571 Hz.

    The ear identifies AE vs AH primarily
    by F2, not F1.
    AH F2 = 1190 Hz.
    1571 Hz is perceptually closer to AH
    than to AE. The listener hears "um."

    No blend factor applied to a target
    of 900 Hz will preserve AE identity.
    The target was wrong, not the factor.

  THE CORRECT PHYSICS (revised):

    During anticipatory nasalization,
    the ORAL formants change very little
    until the physical closure occurs.
    What changes is:
      - A low-amplitude nasal murmur
        is ADDED (velum opening). ← FIX 12C
      - F1 drops slightly (jaw closes
        fractionally as lips approach).
      - F2 is nearly UNCHANGED until
        the closure is complete.

    The dominant vowel identity (F2)
    is preserved through the anticipatory
    phase. Only F1 moves, and only slightly.

  THE FIX — rev3:

    PER-FORMANT BLEND FACTORS:
      F1 blend: 0.12  (small jaw closure)
      F2 blend: 0.00  (F2 unchanged — key)
      F3 blend: 0.00
      F4 blend: 0.00

    For stops: same principle.
      F1 blend: 0.08
      F2 blend: 0.00

    For L: F2 blend 0.15 (lateral
      does genuinely lower F2 slightly
      during the vowel — less than before).

    FIX 12C unchanged from rev2.
    FIX 12A unchanged from rev2
    (COART_DUR_COMPRESS = 0.88).

  All v13 fixes unchanged.
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
# FIX 12 CONSTANTS — REVISION 3
# ============================================================

CLOSING_PHS = {
    'M', 'N', 'NG',
    'B', 'D', 'G', 'P', 'T', 'K',
    'L',
}
NASAL_CLOSING_PHS = {'M', 'N', 'NG'}
STOP_CLOSING_PHS  = {
    'B', 'D', 'G', 'P', 'T', 'K'}

# Vowel duration compression.
# 0.88 — only 12% of duration lost.
COART_DUR_COMPRESS = 0.88

# Nasal murmur additive gain.
# Low — colors without darkening.
NASAL_ANTICIPATION_GAIN = 0.07
NASAL_ANTICIPATION_MS   = 28.0

# Nasal tract resonance �� additive
# murmur only (FIX 12C). NOT used
# as F_end blend target.
NASAL_MURMUR_F = [250.0, 1000.0,
                   2200.0, 3300.0]
NASAL_MURMUR_B = [ 80.0,  150.0,
                    200.0,  250.0]

# ── PER-FORMANT BLEND FACTORS ────────────
#
# REVISION 3: Apply blend per-formant.
# F2 identity is preserved (blend=0).
# Only F1 moves slightly.
#
# Nasals (M, N, NG):
#   F1: small jaw/lip closure movement
#   F2: ZERO — vowel identity preserved
NASAL_BLEND_PER_FORMANT = [0.12, 0.00,
                             0.00, 0.00]

# Stops (B, D, G, P, T, K):
#   F1: tiny movement
#   F2: ZERO
STOP_BLEND_PER_FORMANT  = [0.08, 0.00,
                             0.00, 0.00]

# Lateral (L):
#   F2 does lower slightly into L —
#   less than before, but non-zero.
L_BLEND_PER_FORMANT     = [0.08, 0.15,
                             0.00, 0.00]

# Oral closure approach targets.
# These matter only for F1 now
# since F2+ blends are 0.
# F1 targets: where jaw/lips are heading.
NASAL_CLOSURE_F1 = {
    'M':  550,   # bilabial — lip closure
    'N':  510,   # alveolar — tongue tip up
    'NG': 490,   # velar — tongue back up
}


# ============================================================
# FIX 12A: VOWEL DURATION COMPRESSION
# ============================================================

def _coart_compress_dur(dur_ms, ph,
                         next_ph):
    if next_ph not in CLOSING_PHS:
        return dur_ms
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return dur_ms
    return dur_ms * COART_DUR_COMPRESS


# ============================================================
# FIX 12B: FORMANT TRAJECTORY CLOSURE
# Per-formant blending.
# F2 identity preserved.
# ============================================================

def _coart_f_end(ph, next_ph,
                  current_f, current_b):
    """
    Per-formant blend toward closure.

    CRITICAL: F2 blend is 0.00 for nasals
    and stops. The vowel identity (which
    the ear reads primarily from F2) is
    not changed during the anticipatory
    phase. Only F1 moves slightly.

    For AE (F2=1720) before M:
      Old (broken): F2 → 1571 (heard as AH)
      New (correct): F2 → 1720 (AE preserved)
    """
    if next_ph not in CLOSING_PHS:
        return None, None
    if ph not in VOWEL_PHONEMES and \
       ph not in DIPHTHONG_PHONEMES:
        return None, None

    n_f = len(current_f)

    if next_ph in NASAL_CLOSING_PHS:
        blends = NASAL_BLEND_PER_FORMANT
        f1_tgt = NASAL_CLOSURE_F1.get(
            next_ph, 510)
        f_end = []
        b_end = []
        for i in range(n_f):
            b = blends[i] \
                if i < len(blends) else 0.0
            if i == 0:
                # F1: blend toward closure
                f_end.append(
                    current_f[0] * (1 - b)
                    + f1_tgt * b)
            else:
                # F2, F3, F4: unchanged
                f_end.append(current_f[i])
            b_end.append(current_b[i])
        return f_end, b_end

    if next_ph in STOP_CLOSING_PHS:
        blends = STOP_BLEND_PER_FORMANT
        f_end = []
        b_end = []
        for i in range(n_f):
            b = blends[i] \
                if i < len(blends) else 0.0
            if i == 0 and b > 0:
                tgt = NEUTRAL_F[0] \
                      if 0 < len(NEUTRAL_F) \
                      else current_f[0]
                f_end.append(
                    current_f[0] * (1 - b)
                    + tgt * b)
            else:
                f_end.append(current_f[i])
            b_end.append(current_b[i])
        return f_end, b_end

    if next_ph == 'L':
        blends = L_BLEND_PER_FORMANT
        f_end = list(current_f)
        b_end = list(current_b)
        for i in range(n_f):
            b = blends[i] \
                if i < len(blends) else 0.0
            if b > 0:
                if i == 0:
                    tgt = NEUTRAL_F[0] \
                          if 0 < len(NEUTRAL_F) \
                          else current_f[0]
                elif i == 1:
                    tgt = 1000.0
                else:
                    tgt = current_f[i]
                f_end[i] = (
                    current_f[i] * (1 - b)
                    + tgt * b)
        return f_end, b_end

    return None, None


def _build_trajectories_v14(
        phoneme_specs, sr=SR):
    """
    v14 trajectory builder.
    Per-formant coarticulation blend.
    F2 identity preserved for nasals/stops.
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
                # B_end: leave unchanged
                # (bandwidth shift is minor)

        patched.append(s)

    return _build_trajectories(
        patched, sr=sr)


# ============================================================
# FIX 12C: NASAL MURMUR (unchanged)
# ============================================================

def _apply_nasal_anticipation(
        out, specs, sr=SR):
    """
    Additive nasal murmur in vowel tail
    before M/N/NG.
    Gain = 0.07 — colors without darkening.
    The oral vowel signal is NOT modified.
    The murmur is purely additive.
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

            env = np.linspace(0.0, 1.0, n_m)
            out[murmur_start:murmur_end] \
                = f32(
                    out[murmur_start:
                        murmur_end].astype(
                        np.float64)
                    + murmur * env)

        pos += n_s

    return out


# ============================================================
# OLA STRETCH
# ============================================================

def _ola_stretch(sig, factor,
                  win_ms=25, sr=SR):
    sig     = np.array(sig, dtype=np.float64)
    n_in    = len(sig)
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 != 0:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    if hop_out == 0:
        hop_out = 1
    n_frames = max(1,
        (n_in - win_n) // hop_in + 1)
    n_out = hop_out * (n_frames - 1) + win_n
    out   = np.zeros(n_out, dtype=np.float64)
    norm  = np.zeros(n_out, dtype=np.float64)
    window = np.hanning(win_n)
    for i in range(n_frames):
        i0 = i * hop_in
        i1 = i0 + win_n
        if i1 > n_in:
            frame = np.zeros(win_n)
            av = n_in - i0
            if av > 0:
                frame[:av] = sig[i0:i0 + av]
        else:
            frame = sig[i0:i1]
        o0 = i * hop_out
        o1 = o0 + win_n
        out[o0:o1]  += frame * window
        norm[o0:o1] += window
    norm = np.where(norm < 1e-8, 1.0, norm)
    return f32(out / norm)


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

        # FIX 12A
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

    # FIX 12B
    F_full, B_full, _ = \
        _build_trajectories_v14(
            specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass(
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

    # Nasal antiformants — unchanged.
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
                    np.cos(2 * np.pi * af * T))
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

    # FIX 12C
    out = _apply_nasal_anticipation(
        out, specs, sr=sr)

    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos + n_s] *= item['amp']
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
    print("VOICE PHYSICS v14 — rev3")
    print("per-formant blend: F2 preserved")
    print()
    print("  NASAL_BLEND_PER_FORMANT:",
          NASAL_BLEND_PER_FORMANT)
    print("  F2 blend = 0.00 — AE identity kept")
    print("  F1 blend = 0.12 — jaw closure only")
    print()
    print("  AE before M:")
    ae_f = VOWEL_F['AE'][0]
    f1_blend = NASAL_BLEND_PER_FORMANT[0]
    f2_blend = NASAL_BLEND_PER_FORMANT[1]
    f1_tgt   = NASAL_CLOSURE_F1['M']
    f1_result = ae_f[0]*(1-f1_blend) + f1_tgt*f1_blend
    f2_result = ae_f[1]*(1-f2_blend) + ae_f[1]*f2_blend
    print(f"    F1: {ae_f[0]} → {f1_result:.0f}Hz "
          f"(target {f1_tgt}Hz)")
    print(f"    F2: {ae_f[1]} → {f2_result:.0f}Hz "
          f"(unchanged — AE identity)")
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
    save("v14r3_i_am_here",
         seg, rt60=1.4, dr=0.52)

    seg_slow = _ola_stretch(
        synth_phrase(
            [('I',    ['AY']),
             ('am',   ['AE', 'M']),
             ('here', ['H',  'IY', 'R'])],
            punctuation='.',
            add_breath=False),
        factor=3.5)
    save("v14r3_i_am_here_slow",
         seg_slow, rt60=1.4, dr=0.52)

    print()
    print("  Isolation: am / ham / him / sun")
    for word, phones in [
        ('am',   ['AE', 'M']),
        ('ham',  ['HH', 'AE', 'M']),
        ('him',  ['HH', 'IH', 'M']),
        ('sun',  ['S',  'AH', 'N']),
        ('ring', ['R',  'IH', 'NG']),
    ]:
        seg = synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_breath=False)
        save(f"v14r3_{word}",
             seg, rt60=0.8, dr=0.65)

        seg_s = _ola_stretch(
            synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False),
            factor=4.0)
        save(f"v14r3_{word}_slow",
             seg_s, rt60=0.6, dr=0.72)

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
        arc_type=ARC_NORMAL)
    save("v14r3_the_voice_was_already_here",
         seg, rt60=1.5, dr=0.50)

    print()
    print("=" * 52)
    print()
    print("  PLAY:")
    print("  afplay output_play/v14r3_i_am_here.wav")
    print("  afplay output_play/v14r3_i_am_here_slow.wav")
    print("  afplay output_play/v14r3_am.wav")
    print("  afplay output_play/v14r3_am_slow.wav")
    print("  afplay output_play/v14r3_ham.wav")
    print()
    print("  IF STILL HEARING 'um':")
    print("    → The problem is NOT coarticulation.")
    print("    → Disable FIX 12 entirely to confirm.")
    print("    → Set COART_DUR_COMPRESS = 1.0")
    print("      and NASAL_ANTICIPATION_GAIN = 0.0")
    print("    → If still 'um': bug is in v13 or")
    print("      the AE transcription itself.")
    print("    → Check 'am' is ['AE','M'],")
    print("      not ['AH','M'].")
    print()
