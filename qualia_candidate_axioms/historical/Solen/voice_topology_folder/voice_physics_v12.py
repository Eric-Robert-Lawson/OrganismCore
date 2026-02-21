"""
VOICE PHYSICS v12 — rev12
February 2026

CHANGES FROM v11:

  FIX 7: VOT (voice onset time) uses flat
    broadband noise regardless of following
    vowel.
    Physical truth: VOT = voiceless airflow
    through a tract already configured for
    the following vowel. This is the same
    physical event as H. The fix applied to
    H in v11 applies equally here.
    Fix: _make_vot_noise() replaces the
    noise_full slice in the stop VOT zone.
    It calls _h_formant_filter() with the
    following phoneme's formant values —
    exactly as _make_h_bypass() does.
    Result: T before UW sounds like H before
    UW. "To" and "who" now share the same
    voiceless onset spectral character.
    "Tate" and "hate" share the same
    EY-colored aspiration.

  FIX 8: Nasal release noise absent.
    N/M/NG releasing into a vowel was modeled
    as a direct formant trajectory transition
    with no acoustic release event.
    Physical truth: the tongue/lips releasing
    from nasal closure produces ~10-20ms of
    turbulent onset noise — voiceless or
    near-voiceless — filtered through the
    tract already moving toward the vowel.
    This is why "near" and "hear" are
    acoustically related: both begin with
    vowel-colored onset noise, one just
    15ms of it, one 100ms.
    Fix: _make_nasal_release() generates
    a brief turbulent burst at the onset of
    the vowel following a nasal. Added as
    a bypass_seg at the vowel's start
    position. Duration: 12-18ms. Gain: low
    (~0.12). Formant-colored via
    _h_formant_filter() with widened BW
    (the constriction is opening, not open).

  All v11 fixes preserved unchanged.
"""

from voice_physics_v9 import (
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
)

import numpy as np
from scipy.signal import lfilter, butter
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v12-rev12'


# ============================================================
# CONSTANTS — all v11 constants preserved
# ============================================================

PHRASE_ATK_MS       = 25

DH_TRACT_BYPASS_MS  = 25
DH_BYPASS_BP_LO     = 1800
DH_BYPASS_BP_HI     = 6500
DH_BYPASS_GAIN      = 0.35
DH_BYPASS_ATK_MS    = 18
DH_BW_MULT          = 3.0
DH_BUZZ_GAIN        = 0.45
DH_BUZZ_ATK_MS      = 18

H_BYPASS_HP_HZ      = 200
H_BYPASS_LP_HZ      = 1500
H_BYPASS_LP_ORDER   = 2
H_BYPASS_GAIN       = 0.55
H_BYPASS_ATK_MS     = 30

H_USE_NEXT_FORMANTS  = True
H_NASAL_FORMANTS     = [250, 1000, 2200, 3300, 4000]
H_NASAL_BW           = [ 80,  150,  200,  250,  300]
H_NASAL_PHS          = {'M', 'N', 'NG'}
H_STOP_PHS           = {'P', 'B', 'T', 'D', 'K', 'G',
                         'CH', 'JH'}

Z_BYPASS_GAIN_FLOOR  = 0.35
ZH_BYPASS_GAIN_FLOOR = 0.40

FRIC_BUZZ_GAINS = {
    'DH': 0.45,
    'Z':  1.20,
    'ZH': 0.30,
    'V':  0.25,
}
FRIC_BUZZ_GAIN_DEFAULT = 0.20

V_BYPASS_BP_LO = 800
V_BYPASS_BP_HI = 2200

FINAL_FRIC_MAX_MS = 100

VOICED_TO_H_CROSSFADE_MS = 25

SIBILANT_VOICED_RATIO = 0.80
RELATIVE_SCALE_PHS    = {'S', 'Z', 'SH', 'ZH'}

NORM_PERCENTILE = 90
NORM_TARGET     = 0.88
VOWEL_SET = set(
    'AA AE AH AO AW AY EH ER IH IY '
    'OH OW OY UH UW L R W Y M N NG'
    .split())

RESONATOR_CFG_V10 = {
    'S':  {'fc': 8800, 'bw': 1200},
    'Z':  {'fc': 8000, 'bw': 1200},
    'SH': {'fc': 2500, 'bw':  900},
    'ZH': {'fc': 2200, 'bw':  900},
}

BREATH_BASE_MS             = 50
BREATH_MAX_MS              = 100
BREATH_BASE_AMP            = 0.08
BREATH_WEIGHT_AMP          = 0.18
BREATH_SCALE_MS_PER_PHONE  = 4.0

ARC_NORMAL  = 'normal'
ARC_WEIGHT  = 'weight'
ARC_EUREKA  = 'eureka'
ARC_GRIEF   = 'grief'
ARC_CONTAIN = 'containment'
ARC_RECOGN  = 'recognition'

# ============================================================
# FIX 7: VOT coarticulation constants
# VOT noise colored by following vowel.
# Aspirated stops only (unvoiced + voiced
# with long VOT). Voiced stops have near-zero
# VOT — skip coloring for B/D/G.
# ============================================================

VOT_COLOR_PHS = {'P', 'T', 'K', 'CH'}
# B/D/G have short or pre-voiced VOT —
# formant coloring is less audible there.
# Keep flat for now; revisit in v13.

# ============================================================
# FIX 8: Nasal release constants
# Brief turbulent onset after nasal → vowel.
# ============================================================

NASAL_RELEASE_MS   = 15    # duration ms
NASAL_RELEASE_GAIN = 0.10  # amplitude
# BW multiplier: constriction opening,
# not fully open. Wider BW = more turbulent,
# less resonant than stable H.
NASAL_RELEASE_BW_MULT = 2.5

NASAL_CONSONANTS = {'M', 'N', 'NG'}

VOWELS_AND_APPROX = set(
    'AA AE AH AO AW AY EH ER IH IY '
    'OH OW OY UH UW L R W Y M N NG'
    .split())


# ============================================================
# SHARED HELPER: get next phoneme's formants
# Used by both VOT coloring (FIX 7) and
# nasal release (FIX 8) — same lookup as H.
# ============================================================

def _get_coart_formants(next_ph):
    """
    Return (freqs, bws) for coarticulation
    noise coloring toward next_ph.

    Returns (None, None) if next_ph has no
    stable tract configuration to preview
    (stops, unknown).

    Same logic as _make_h_bypass() routing.
    """
    if next_ph is None:
        return None, None
    if next_ph in H_NASAL_PHS:
        return list(H_NASAL_FORMANTS), \
               list(H_NASAL_BW)
    if next_ph in VOWEL_F:
        freqs = list(VOWEL_F[next_ph])
        try:
            bws = [get_b(next_ph, i)
                   for i in range(len(freqs))]
        except Exception:
            bws = [80, 90, 120,
                   150, 200][:len(freqs)]
        return freqs, bws
    return None, None


# ============================================================
# CAVITY RESONATOR (v10, unchanged)
# ============================================================

def _cavity_resonator_v10(noise, ph, sr=SR):
    if ph in RESONATOR_CFG_V10:
        cfg = RESONATOR_CFG_V10[ph]
    elif ph in RESONATOR_CFG:
        cfg = RESONATOR_CFG[ph]
    else:
        return noise
    return cavity_resonator(
        noise, cfg['fc'], cfg['bw'], sr=sr)


# ============================================================
# BREATH MODEL (v11, unchanged)
# ============================================================

def breath_model(phrase_len_ms,
                  arc_type=ARC_NORMAL,
                  sr=SR):
    n_phones_approx = max(1,
        phrase_len_ms / 80.0)
    dur_ms = min(
        BREATH_BASE_MS +
        n_phones_approx *
        BREATH_SCALE_MS_PER_PHONE,
        BREATH_MAX_MS)
    if arc_type == ARC_WEIGHT:
        depth  = BREATH_WEIGHT_AMP
        dur_ms = min(dur_ms * 1.4,
                     BREATH_MAX_MS)
    elif arc_type == ARC_GRIEF:
        depth  = BREATH_BASE_AMP * 0.6
        dur_ms = dur_ms * 0.5
    elif arc_type == ARC_CONTAIN:
        depth  = BREATH_BASE_AMP * 0.4
        dur_ms = dur_ms * 0.6
    else:
        depth  = BREATH_BASE_AMP
    return float(dur_ms), float(depth)


def _make_breath_onset(phrase_len_ms,
                        arc_type=ARC_NORMAL,
                        sr=SR):
    dur_ms, depth = breath_model(
        phrase_len_ms,
        arc_type=arc_type, sr=sr)
    n_s = max(1, int(dur_ms / 1000.0 * sr))
    noise = f32(np.random.normal(0, 1, n_s))
    try:
        b, a  = safe_hp(200, sr)
        noise = f32(lfilter(b, a, noise))
    except Exception:
        pass
    try:
        nyq  = sr * 0.5
        wn   = min(3000.0 / nyq, 0.97)
        b, a = butter(2, wn, btype='low')
        noise = f32(lfilter(b, a, noise))
    except Exception:
        pass
    noise = calibrate(noise) * depth
    atk = n_s // 3
    rel = n_s // 4
    env = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))
    if arc_type == ARC_GRIEF:
        jitter = f32(np.random.normal(
            1.0, 0.15, n_s))
        jitter = np.clip(jitter, 0.2, 1.8)
        noise  = noise * f32(jitter)
    return f32(noise * env)


# ============================================================
# H FORMANT FILTER (v11, unchanged)
# Core IIR cascade. Now also used by
# VOT coloring and nasal release.
# ============================================================

def _h_formant_filter(noise, freqs, bws,
                       sr=SR):
    """
    Filter noise through IIR resonator cascade.
    float64 throughout. Validates each stage.
    Used by: H bypass, VOT coloring, nasal
    release — any voiceless coarticulation
    noise that should carry the following
    phoneme's spectral character.
    """
    T   = 1.0 / sr
    sig = np.asarray(noise,
                     dtype=np.float64)
    sig = np.nan_to_num(
        sig, nan=0.0,
        posinf=0.0, neginf=0.0)
    for fc, bw in zip(freqs, bws):
        fc = float(fc)
        bw = float(bw)
        if fc <= 0 or bw <= 0 or \
           fc >= sr * 0.499:
            continue
        pole_r = np.exp(-np.pi * bw * T)
        if pole_r >= 1.0 or pole_r <= 0.0:
            continue
        cos_t = np.cos(2 * np.pi * fc * T)
        a1    =  2.0 * pole_r * cos_t
        a2    = -(pole_r ** 2)
        b0    = 1.0 - a1 - a2
        if not (np.isfinite(b0)
                and np.isfinite(a1)
                and np.isfinite(a2)):
            continue
        stage = lfilter(
            [b0], [1.0, -a1, -a2], sig)
        if not np.all(np.isfinite(stage)):
            continue
        sig = stage
    return f32(np.nan_to_num(
        sig, nan=0.0,
        posinf=0.0, neginf=0.0))


# ============================================================
# H BYPASS (v11, unchanged)
# ============================================================

def _make_h_bypass(n_s, sr=SR,
                    next_is_vowel=False,
                    next_ph=None,
                    onset_offset=0):
    n_s   = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))
    shaped = None
    if H_USE_NEXT_FORMANTS and \
       next_ph is not None and \
       next_ph not in H_STOP_PHS:
        freqs, bws = _get_coart_formants(
            next_ph)
        if freqs is not None:
            try:
                shaped = _h_formant_filter(
                    noise, freqs, bws, sr=sr)
                shaped = (calibrate(shaped)
                          * H_BYPASS_GAIN)
            except Exception:
                shaped = None
    if shaped is None:
        try:
            b, a  = safe_hp(
                H_BYPASS_HP_HZ, sr)
            broad = f32(lfilter(b, a, noise))
        except Exception:
            broad = noise.copy()
        try:
            nyq  = sr * 0.5
            wn   = min(
                H_BYPASS_LP_HZ / nyq, 0.98)
            b, a = butter(
                H_BYPASS_LP_ORDER,
                wn, btype='low')
            broad = f32(lfilter(b, a, broad))
        except Exception:
            pass
        shaped = (calibrate(broad)
                  * H_BYPASS_GAIN)
    rel_ms = 20 if next_is_vowel else 12
    rel    = min(
        int(rel_ms / 1000.0 * sr),
        n_s // 4)
    atk    = min(
        int(H_BYPASS_ATK_MS / 1000.0 * sr),
        n_s // 3)
    env    = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))
    if len(shaped) < n_s:
        shaped = np.pad(
            shaped,
            (0, n_s - len(shaped)))
    shaped = shaped[:n_s]
    raw = f32(shaped * env)
    if onset_offset > 0:
        onset_offset = min(onset_offset, n_s)
        out       = np.zeros(n_s, dtype=DTYPE)
        remaining = n_s - onset_offset
        if remaining > 0:
            out[onset_offset:] = \
                raw[:remaining]
        return f32(out)
    return raw


# ============================================================
# FIX 7: VOT COARTICULATION NOISE
#
# Replaces noise_full slice in the VOT zone
# for aspirated stops (P T K CH).
#
# Physical truth: VOT = voiceless turbulent
# airflow through a tract already configured
# for the following vowel. Identical physical
# mechanism to H. Should carry identical
# spectral character.
#
# "To" before UW: VOT noise colored by UW
#   formants (F1=310, F2=870 — dark, back).
# "Tate" before EY: VOT noise colored by EY
#   formants (F1=530, F2=1840 — mid, front).
# These now match the H before UW / H before
# EY spectral signatures from v11.
# ============================================================

def _make_vot_noise(n_vot, next_ph,
                     sr=SR):
    """
    Generate VOT noise colored by next_ph
    formant configuration.

    For aspirated stops (P T K CH) before
    a vowel or sonorant: use formant cascade.
    Fallback: HP-filtered broadband (same as
    pre-v12 behavior).

    n_vot: number of samples for VOT zone.
    next_ph: following phoneme.
    Returns: f32 array of length n_vot,
             calibrated, no envelope applied.
             Caller blends with voiced source.
    """
    n_vot = int(n_vot)
    if n_vot <= 0:
        return f32(np.zeros(n_vot))

    noise = calibrate(
        f32(np.random.normal(0, 1, n_vot)))

    freqs, bws = _get_coart_formants(next_ph)

    if freqs is not None:
        try:
            colored = _h_formant_filter(
                noise, freqs, bws, sr=sr)
            return calibrate(f32(colored))
        except Exception:
            pass

    # Fallback: HP at burst_hp frequency
    # (original behavior)
    try:
        b, a = safe_hp(2000, sr)
        broad = f32(lfilter(b, a, noise))
        return calibrate(broad)
    except Exception:
        return noise


# ============================================================
# FIX 8: NASAL RELEASE NOISE
#
# Brief turbulent onset added at the start
# of a vowel that immediately follows a
# nasal consonant.
#
# Physical truth: tongue/lips releasing from
# nasal closure → brief constriction opening
# → turbulent noise, ~10-20ms, colored by
# the vowel formants (with wider BW because
# the constriction is opening, not open).
#
# This is why "near" and "hear" are
# acoustically related. "Near": 15ms of
# vowel-colored onset noise from the N
# release. "Hear": 100ms of vowel-colored
# onset noise from the H. Same mechanism,
# different duration.
#
# Added as bypass_seg at the vowel's sample
# start position. Does not alter the tract
# source signal itself.
# ============================================================

def _make_nasal_release(n_release,
                         next_ph,
                         sr=SR):
    """
    Generate nasal release noise burst.

    n_release: number of samples (~12-18ms).
    next_ph: vowel being released into.
    Returns: f32 array, length n_release.

    Formant coloring: uses _h_formant_filter()
    with BW widened by NASAL_RELEASE_BW_MULT.
    The constriction is mid-opening, not at
    the stable vowel configuration. Wider BW
    = less resonant, more turbulent —
    physically correct for a constriction
    that is still closing.
    """
    n_release = int(n_release)
    if n_release <= 0:
        return f32(np.zeros(n_release))

    noise = calibrate(
        f32(np.random.normal(0, 1, n_release)))

    freqs, bws = _get_coart_formants(next_ph)

    if freqs is not None:
        # Widen BW: constriction opening,
        # not fully open
        bws_wide = [
            b * NASAL_RELEASE_BW_MULT
            for b in bws]
        try:
            colored = _h_formant_filter(
                noise, freqs,
                bws_wide, sr=sr)
            sig = calibrate(f32(colored))
        except Exception:
            sig = noise
    else:
        sig = noise

    # Short envelope: sharp attack, fast
    # decay. This is a release event, not
    # a sustained sound.
    atk = max(1, n_release // 5)
    rel = max(1, n_release // 2)
    env = f32(np.ones(n_release))
    if atk < n_release:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel < n_release:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))

    return f32(sig * env * NASAL_RELEASE_GAIN)


# ============================================================
# DH BYPASS + BUZZ (v11, unchanged)
# ============================================================

def _make_dh_bypass(n_s, sr=SR,
                     next_is_vowel=False,
                     onset_delay=0):
    n_s         = int(n_s)
    onset_delay = max(0, int(onset_delay))
    if onset_delay >= n_s:
        return f32(np.zeros(n_s))
    n_eff = n_s - onset_delay
    noise = calibrate(
        f32(np.random.normal(0, 1, n_eff)))
    nyq = sr * 0.5
    try:
        lo  = max(DH_BYPASS_BP_LO, 20) / nyq
        hi  = min(DH_BYPASS_BP_HI,
                  sr * 0.48) / nyq
        lo  = min(lo, 0.97)
        hi  = min(hi, 0.98)
        if lo < hi:
            b, a   = butter(2, [lo, hi],
                            btype='band')
            shaped = f32(lfilter(b, a, noise))
        else:
            shaped = noise
    except Exception:
        shaped = noise
    shaped = calibrate(shaped) * DH_BYPASS_GAIN
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(
        int(rel_ms / 1000.0 * sr), n_eff // 4)
    atk    = min(
        int(DH_BYPASS_ATK_MS / 1000.0 * sr),
        n_eff // 3)
    env    = f32(np.ones(n_eff))
    if atk > 0 and atk < n_eff:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1, 0, rel))
    raw = np.zeros(n_s, dtype=DTYPE)
    raw[onset_delay:] = f32(shaped * env)
    return f32(raw)


def _make_dh_buzz(voiced_seg, n_s, sr=SR):
    n_s   = int(n_s)
    n_seg = len(voiced_seg)
    n_use = min(n_s, n_seg)
    buzz  = f32(voiced_seg[:n_use]) * \
            DH_BUZZ_GAIN
    atk = min(
        int(DH_BUZZ_ATK_MS / 1000.0 * sr),
        n_use // 3)
    env = f32(np.ones(n_use))
    if atk > 0 and atk < n_use:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    raw = np.zeros(n_s, dtype=DTYPE)
    raw[:n_use] = f32(buzz * env)
    return f32(raw)


# ============================================================
# V BYPASS (v11, unchanged)
# ============================================================

def _make_v_bypass(n_eff, gain, sr=SR):
    noise = calibrate(
        f32(np.random.normal(0, 1, n_eff)))
    nyq = sr * 0.5
    try:
        lo  = max(V_BYPASS_BP_LO, 20) / nyq
        hi  = min(V_BYPASS_BP_HI,
                  sr * 0.48) / nyq
        lo  = min(lo, 0.97)
        hi  = min(hi, 0.98)
        if lo < hi:
            b, a  = butter(2, [lo, hi],
                           btype='band')
            broad = f32(lfilter(b, a, noise))
        else:
            broad = noise.copy()
    except Exception:
        broad = noise.copy()
    return calibrate(broad) * gain


# ============================================================
# GENERAL BYPASS (v11, unchanged)
# ============================================================

def _make_bypass(ph, n_s, sr=SR,
                  next_is_vowel=False,
                  onset_delay=0,
                  voiced_rms=None,
                  next_ph=None,
                  onset_offset=0):
    if ph == 'DH':
        return _make_dh_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            onset_delay=onset_delay)
    if ph == 'H':
        return _make_h_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            next_ph=next_ph,
            onset_offset=onset_offset)
    gains = get_calibrated_gains_v8(sr=sr)
    gain  = gains.get(ph, None)
    if ph == 'Z':
        if gain is None or \
           gain < Z_BYPASS_GAIN_FLOOR:
            gain = Z_BYPASS_GAIN_FLOOR
    elif ph == 'ZH':
        if gain is None or \
           gain < ZH_BYPASS_GAIN_FLOOR:
            gain = ZH_BYPASS_GAIN_FLOOR
    n_s         = int(n_s)
    onset_delay = max(0, int(onset_delay))
    if onset_delay >= n_s:
        return f32(np.zeros(n_s))
    n_eff  = n_s - onset_delay
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(
        int(rel_ms / 1000.0 * sr),
        n_eff // 4)
    atk    = min(int(0.005 * sr), n_eff // 4)

    def _env(sig):
        env = f32(np.ones(n_eff))
        if atk > 0 and atk < n_eff:
            env[:atk] = f32(
                np.linspace(0, 1, atk))
        if rel > 0:
            env[-rel:] = f32(
                np.linspace(1, 0, rel))
        return f32(sig * env)

    raw = np.zeros(n_s, dtype=DTYPE)
    if ph in RESONATOR_CFG_V10 or \
       ph in RESONATOR_CFG:
        g = (gain if gain is not None
             else (RESONATOR_CFG_V10
                   .get(ph,
                        RESONATOR_CFG
                        .get(ph, {}))
                   .get('gain', 0.3)))
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        res   = _cavity_resonator_v10(
            noise, ph, sr=sr)
        sib   = calibrate(res)
        if ph in RELATIVE_SCALE_PHS and \
           voiced_rms is not None and \
           voiced_rms > 1e-8:
            sib_rms = float(np.sqrt(
                np.mean(sib**2) + 1e-12))
            if sib_rms > 1e-8:
                sib = sib * (
                    voiced_rms *
                    SIBILANT_VOICED_RATIO /
                    sib_rms)
        else:
            sib = sib * g
        raw[onset_delay:] = _env(sib)
    elif ph == 'V':
        g   = (gain if gain is not None
               else 0.14)
        sib = _make_v_bypass(n_eff, g, sr=sr)
        if voiced_rms is not None and \
           voiced_rms > 1e-8:
            sib_rms = float(np.sqrt(
                np.mean(sib**2) + 1e-12))
            if sib_rms > 1e-8:
                sib = sib * (
                    voiced_rms *
                    SIBILANT_VOICED_RATIO /
                    sib_rms)
        raw[onset_delay:] = _env(sib)
    elif ph in BROADBAND_CFG:
        cfg   = BROADBAND_CFG[ph]
        g     = (gain if gain is not None
                 else cfg['gain'])
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        try:
            b, a  = safe_hp(cfg['hp_fc'], sr)
            broad = f32(lfilter(b, a, noise))
        except Exception:
            broad = noise.copy()
        sib = calibrate(broad)
        if ph in RELATIVE_SCALE_PHS and \
           voiced_rms is not None and \
           voiced_rms > 1e-8:
            sib_rms = float(np.sqrt(
                np.mean(sib**2) + 1e-12))
            if sib_rms > 1e-8:
                sib = sib * (
                    voiced_rms *
                    SIBILANT_VOICED_RATIO /
                    sib_rms)
        else:
            sib = sib * g
        raw[onset_delay:] = _env(sib)
    return f32(raw)


# ============================================================
# TRAJECTORY BUILDER (v11, unchanged)
# H passes through — no forced NEUTRAL_F.
# ============================================================

def _build_trajectories(phoneme_specs,
                         sr=SR):
    patched = []
    for spec in phoneme_specs:
        ph = spec['ph']
        if ph == 'H':
            patched.append(spec)
        elif ph == 'DH':
            s = copy.copy(spec)
            s['bw_mult'] = (
                s.get('bw_mult', 1.0) *
                DH_BW_MULT)
            patched.append(s)
        else:
            patched.append(spec)
    return build_trajectories(patched, sr=sr)


# ============================================================
# SOURCE BUILDER
# FIX 7: VOT noise replaced with
#   _make_vot_noise() for aspirated stops.
# FIX 8: Nasal release bypass_seg added
#   at vowel onset after nasal consonant.
# ============================================================

def _build_source_and_bypass(
        phoneme_specs, sr=SR):

    n_total = sum(
        s['n_s'] for s in phoneme_specs)

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

    UNVOICED_FRICS = {'S', 'SH', 'F', 'TH'}

    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []
    buzz_segs    = []

    phrase_atk_n = int(
        PHRASE_ATK_MS / 1000.0 * sr)
    n_nasal_rel  = int(
        NASAL_RELEASE_MS / 1000.0 * sr)

    voiced_rms_per_spec = []
    pos = 0
    for spec in phoneme_specs:
        n_s    = spec['n_s']
        n_on_  = min(trans_n(
            spec['ph'], sr), n_s // 3)
        n_off_ = min(trans_n(
            spec['ph'], sr), n_s // 3)
        n_bod  = max(1,
                     n_s - n_on_ - n_off_)
        body_s = pos + n_on_
        body_e = body_s + n_bod
        v_seg  = voiced_full[body_s:body_e]
        vrms   = float(np.sqrt(
            np.mean(v_seg**2) + 1e-12))
        voiced_rms_per_spec.append(vrms)
        pos += n_s

    n_specs = len(phoneme_specs)

    # Track previous phoneme for nasal
    # release detection
    prev_ph = None

    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source', 'voiced')
        s = pos
        e = pos + n_s

        next_ph = (phoneme_specs[si+1]['ph']
                   if si < n_specs-1
                   else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        n_on   = min(
            trans_n(ph, sr), n_s // 3)
        n_off  = min(
            trans_n(ph, sr), n_s // 3)
        n_body = max(0,
                     n_s - n_on - n_off)

        is_phrase_initial = (si == 0)

        if si > 0:
            ref_vrms = \
                voiced_rms_per_spec[si-1]
        elif si < n_specs-1:
            ref_vrms = \
                voiced_rms_per_spec[si+1]
        else:
            ref_vrms = None

        if stype == 'voiced':
            seg = voiced_full[s:e].copy()
            if next_ph in UNVOICED_FRICS:
                zero_start = max(0,
                                 n_s - n_off)
                if zero_start < n_s:
                    seg[zero_start:] = f32(
                        np.linspace(
                            float(seg[
                                zero_start]),
                            0.0,
                            n_s - zero_start))
            if next_ph == 'H':
                xfade_n = min(
                    int(VOICED_TO_H_CROSSFADE_MS
                        / 1000.0 * sr),
                    n_s // 2)
                if xfade_n > 0:
                    fade_start = \
                        n_s - xfade_n
                    seg[fade_start:] *= \
                        f32(np.linspace(
                            1.0, 0.0,
                            n_s - fade_start))
            tract_source[s:e] = seg

            # FIX 8: nasal release
            # If this vowel/sonorant follows
            # a nasal, add release noise at
            # its start position.
            if prev_ph in NASAL_CONSONANTS \
               and ph in VOWELS_AND_APPROX:
                n_rel = min(
                    n_nasal_rel, n_s // 3)
                if n_rel > 0:
                    rel_seg = \
                        _make_nasal_release(
                            n_rel,
                            ph,
                            sr=sr)
                    # Pad to n_s and place
                    # at start of vowel
                    rel_full = np.zeros(
                        n_s, dtype=DTYPE)
                    rel_full[:n_rel] = \
                        rel_seg[:n_rel]
                    bypass_segs.append(
                        (s, f32(rel_full)))

        elif stype == 'h':
            h_onset_offset = (
                phrase_atk_n
                if is_phrase_initial
                else 0)
            byp = _make_h_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel,
                next_ph=next_ph,
                onset_offset=h_onset_offset)
            bypass_segs.append((s, byp))

        elif stype == 'dh':
            buzz = _make_dh_buzz(
                voiced_full[s:e], n_s, sr=sr)
            if is_phrase_initial:
                silence = min(
                    phrase_atk_n, len(buzz))
                buzz[:silence] = 0.0
            buzz_segs.append((s, f32(buzz)))
            byp = _make_dh_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=(
                    phrase_atk_n
                    if is_phrase_initial
                    else 0))
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                buzz_gain = \
                    FRIC_BUZZ_GAINS.get(
                        ph,
                        FRIC_BUZZ_GAIN_DEFAULT)
                amp = np.ones(
                    n_s, dtype=DTYPE)
                fade_start = n_on + n_body
                if n_off > 0 and \
                   fade_start < n_s:
                    amp[fade_start:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                buzz = (voiced_full[s:e] *
                        f32(amp) * buzz_gain)
                buzz_segs.append(
                    (s, f32(buzz)))
            byp = _make_bypass(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=n_on,
                voiced_rms=ref_vrms,
                next_ph=next_ph)
            bypass_segs.append((s, byp))

        elif stype in ('stop_unvoiced',
                        'stop_voiced'):
            clos_n  = spec.get('clos_n',  0)
            burst_n = spec.get('burst_n', 0)
            vot_n   = spec.get('vot_n',   0)
            bamp    = spec.get(
                'burst_amp', 0.28)
            bhp     = spec.get(
                'burst_hp',  2000)
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
                        b, a  = safe_hp(
                            bhp, sr)
                        burst = f32(
                            lfilter(
                                b, a, burst))
                    except Exception:
                        pass
                    benv = f32(np.exp(
                        -np.arange(burst_n) /
                        burst_n * 20))
                    tract_source[
                        s+bs:s+be] = \
                        burst * benv * bamp

            vot_s = clos_n + burst_n
            vot_e = vot_s  + vot_n

            if vot_n > 0 and vot_e <= n_s:
                ne2 = f32(np.linspace(
                    1, 0, vot_n))
                ve2 = 1.0 - ne2

                # FIX 7: VOT coarticulation
                # For aspirated stops, replace
                # flat noise with formant-
                # colored noise from next_ph.
                if ph in VOT_COLOR_PHS and \
                   next_ph is not None:
                    vot_noise = \
                        _make_vot_noise(
                            vot_n,
                            next_ph,
                            sr=sr)
                else:
                    # Original: flat noise_full
                    vot_noise = noise_full[
                        s+vot_s:s+vot_e]\
                        .copy()

                tract_source[
                    s+vot_s:s+vot_e] = (
                    f32(vot_noise) * ne2 +
                    voiced_full[
                        s+vot_s:s+vot_e]
                    * ve2)

            tr_s = vot_e
            if tr_s < n_s:
                tract_source[s+tr_s:e] = \
                    voiced_full[s+tr_s:e]

        prev_ph = ph
        pos += n_s

    return f32(tract_source), \
           bypass_segs, buzz_segs


# ============================================================
# NORMALIZATION (v11, unchanged)
# ============================================================

def _normalize_phrase(signal, specs,
                       prosody, sr=SR):
    signal = f32(signal)
    vowel_samples = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        ph  = spec['ph']
        if ph in VOWEL_SET:
            n_on_  = min(trans_n(ph, sr),
                         n_s // 3)
            n_off_ = min(trans_n(ph, sr),
                         n_s // 3)
            n_bod  = max(1,
                         n_s - n_on_ - n_off_)
            body_s = pos + n_on_
            body_e = min(body_s + n_bod,
                         len(signal))
            if body_e > body_s:
                vowel_samples.append(
                    np.abs(signal[
                        body_s:body_e]))
        pos += n_s
    if vowel_samples:
        ref = np.percentile(
            np.concatenate(vowel_samples),
            NORM_PERCENTILE)
    else:
        ref = np.percentile(
            np.abs(signal), NORM_PERCENTILE)
    if ref > 1e-8:
        signal = signal / ref * NORM_TARGET
    return np.clip(signal, -1.0, 1.0)


# ============================================================
# PHRASE SYNTHESIS (v11 + v12 fixes)
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR,
                  arc_type=ARC_NORMAL,
                  add_breath=True):
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
        FRICS = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH'}
        if word_final and ph in FRICS:
            dur_ms = min(dur_ms,
                         FINAL_FRIC_MAX_MS)
        spec = ph_spec_v9(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            word_final=word_final,
            sr=sr)
        specs.append(spec)

    F_full, B_full, _ = \
        _build_trajectories(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass(specs, sr=sr)

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
            anti    = np.zeros(
                n_s, dtype=DTYPE)
            y1 = y2 = 0.0
            for i in range(n_s):
                a2 = -np.exp(
                    -2*np.pi*abw*T)
                a1 = (2*np.exp(
                    -np.pi*abw*T) *
                      np.cos(
                    2*np.pi*af*T))
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

    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    atk = int(0.025 * sr)
    rel = int(0.055 * sr)
    env = f32(np.ones(n_total))
    if atk > 0 and atk < n_total:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1, 0, rel))
    out = out * f32(amp_env) * env

    segs_out = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s     = spec['n_s']
        segs_out.append(
            out[pos:pos+n_s].copy())
        rest_ms = item.get('rest_ms', 0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(
                    rest_ms, sr=sr))
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
            arc_type=arc_type,
            sr=sr)
        final = f32(np.concatenate(
            [breath_seg, final]))

    return final


# ============================================================
# CONVENIENCE
# ============================================================

def synth_word(word, punct='.',
               pitch=PITCH, dil=DIL,
               sr=SR, add_breath=True):
    syls = WORD_SYLLABLES.get(word.lower())
    if syls is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))
    flat = [p for s in syls for p in s]
    return synth_phrase(
        [(word, flat)],
        punctuation=punct,
        pitch_base=pitch,
        dil=dil, sr=sr,
        add_breath=add_breath)


def save(name, sig, room=True,
          rt60=1.5, dr=0.50, sr=SR):
    sig = f32(sig)
    if room:
        sig = apply_room(
            sig, rt60=rt60, dr=dr, sr=sr)
    write_wav(
        f"output_play/{name}.wav", sig, sr)
    dur = len(sig) / SR
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v12 rev12")
    print()
    print("  FIX 7: VOT coarticulation.")
    print("    T/K/P/CH before vowels: VOT")
    print("    noise colored by following")
    print("    vowel's formant config.")
    print("    'to' and 'who' now share")
    print("    UW-colored onset noise.")
    print("    'tate' and 'hate' share")
    print("    EY-colored aspiration.")
    print()
    print("  FIX 8: Nasal release noise.")
    print("    N/M/NG → vowel: brief 15ms")
    print("    turbulent onset at vowel start.")
    print("    'near' and 'hear' now share")
    print("    IH-colored onset character.")
    print("    Same mechanism, different")
    print("    duration.")
    print()
    print("  All v11 fixes preserved.")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    # Diagnostic phrase: targets both fixes.
    # 'tate': T→EY VOT (FIX 7)
    # 'near': N→IH release (FIX 8)
    # 'here': H→IH bypass (v11 FIX 5)
    # All three should share IH/EY onset
    # character where appropriate.

    PHRASE_MAIN = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L', 'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]

    # Pairs that demonstrate FIX 7 and FIX 8
    DIAGNOSTIC_PAIRS = [
        # FIX 7: T vs H before same vowel
        ('to',   ['T',  'UW']),
        ('who',  ['H',  'UW']),
        ('tate', ['T',  'EY', 'T']),
        ('hate', ['H',  'EY', 'T']),
        # FIX 8: N release vs H before IH
        ('near', ['N',  'IH', 'R']),
        ('hear', ['H',  'IH', 'R']),
        ('rear', ['R',  'IH', 'R']),
    ]

    def ola_stretch(sig, factor,
                    win_ms=25, sr=SR):
        sig    = np.array(sig,
                          dtype=np.float64)
        n_in   = len(sig)
        win_n  = int(win_ms/1000.0*sr)
        if win_n % 2 != 0:
            win_n += 1
        hop_in  = win_n // 4
        hop_out = int(hop_in * factor)
        if hop_out == 0:
            hop_out = 1
        n_frames = max(1,
            (n_in-win_n)//hop_in + 1)
        n_out = hop_out*(n_frames-1)+win_n
        out   = np.zeros(n_out,
                         dtype=np.float64)
        norm  = np.zeros(n_out,
                         dtype=np.float64)
        window = np.hanning(win_n)
        for i in range(n_frames):
            i0 = i * hop_in
            i1 = i0 + win_n
            if i1 > n_in:
                frame = np.zeros(win_n)
                av = n_in - i0
                if av > 0:
                    frame[:av] = \
                        sig[i0:i0+av]
            else:
                frame = sig[i0:i1]
            o0 = i * hop_out
            o1 = o0 + win_n
            out[o0:o1]  += frame * window
            norm[o0:o1] += window
        norm = np.where(
            norm < 1e-8, 1.0, norm)
        return f32(out / norm)

    print("  Full phrase...")
    seg = synth_phrase(
        PHRASE_MAIN,
        punctuation='.',
        pitch_base=PITCH,
        arc_type=ARC_NORMAL)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(f32(seg),
                   rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    print()
    print("  Diagnostic pairs (4x slow)...")
    for word, phones in DIAGNOSTIC_PAIRS:
        sig_w = synth_phrase(
            [(word, phones)],
            pitch_base=PITCH,
            arc_type=ARC_NORMAL,
            add_breath=False)
        sig_w = ola_stretch(
            f32(sig_w), factor=4.0)
        sig_w = apply_room(
            sig_w, rt60=0.6, dr=0.70)
        write_wav(
            f"output_play/slow_{word}.wav",
            sig_w, SR)
        dur = len(sig_w)/SR
        print(f"    slow_{word}.wav  "
              f"({dur:.1f}s)  {phones}")

    print()
    print("  PLAY — diagnostic pairs:")
    print("  Listen for onset character.")
    print("  'to' and 'who' should share")
    print("  dark UW-colored onset noise.")
    print("  'near' and 'hear' should share")
    print("  IH-colored onset character.")
    print()
    for word, _ in DIAGNOSTIC_PAIRS:
        print(f"  afplay output_play/"
              f"slow_{word}.wav")
    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
