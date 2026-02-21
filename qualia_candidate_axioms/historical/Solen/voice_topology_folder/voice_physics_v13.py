"""
VOICE PHYSICS v13 — rev13
February 2026

CHANGES FROM v12:

  FIX 9: F0 trajectory uses piecewise-linear
    interpolation between phoneme pitch anchors,
    producing audible kinks where adjacent
    segments meet at different slopes.
    Fix: replace piecewise-linear f0 construction
    with a cubic spline fitted to per-phoneme
    anchor points at phoneme centers. The spline
    passes smoothly through all anchors. Pitch
    transitions become curves rather than
    broken lines.
    Voiceless phonemes are included as anchor
    points at their natural pitch value so the
    curve remains continuous through silence.
    When voicing resumes after a voiceless
    segment, pitch is already at the correct
    spline value — no jump.
    f0 clipped to [F0_MIN, F0_MAX] after spline
    evaluation to prevent numerical excursion.

  FIX 10: Phrase edge envelope and prosody
    amplitude envelope multiply everywhere,
    causing the phrase to collapse faster than
    intended at the end, especially when the
    final word is already in prosodic decline.
    Fix: separate responsibilities.
    edge_env: phrase boundary only (first 25ms,
      last 55ms). Governs attack and release.
    amp_env: prosody amplitude from plan_prosody.
      Governs the body.
    These no longer both apply to all samples.
    The phrase body is governed by amp_env alone.
    The phrase edges are governed by edge_env.
    Combined at edges only via multiplication.

  FIX 11: Per-word emphasis override.
    synth_phrase() now accepts an optional
    emphasis dict per word entry. Third element
    of each (word, phones, emphasis) tuple.
    emphasis keys:
      'f0_boost': float multiplier on pitch
        (default 1.0). > 1.0 raises pitch.
      'dur_mult': float multiplier on phoneme
        durations (default 1.0). > 1.0 lengthens.
      'amp_boost': float multiplier on amplitude
        (default 1.0). > 1.0 loudens.
    Applied after plan_prosody(), overriding the
    generic contour for marked words.
    This is the minimum needed to say a sentence
    rather than merely produce one.

  All v12 fixes preserved unchanged.
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
from scipy.interpolate import CubicSpline
import copy
import os

os.makedirs("output_play", exist_ok=True)

VOICE_VERSION = 'v13-rev13'


# ============================================================
# CONSTANTS — all v12 constants preserved
# ============================================================

PHRASE_ATK_MS        = 25
PHRASE_REL_MS        = 55

DH_TRACT_BYPASS_MS   = 25
DH_BYPASS_BP_LO      = 1800
DH_BYPASS_BP_HI      = 6500
DH_BYPASS_GAIN       = 0.35
DH_BYPASS_ATK_MS     = 18
DH_BW_MULT           = 3.0
DH_BUZZ_GAIN         = 0.45
DH_BUZZ_ATK_MS       = 18

H_BYPASS_HP_HZ       = 200
H_BYPASS_LP_HZ       = 1500
H_BYPASS_LP_ORDER    = 2
H_BYPASS_GAIN        = 0.55
H_BYPASS_ATK_MS      = 30

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

VOT_COLOR_PHS = {'P', 'T', 'K', 'CH'}

NASAL_RELEASE_MS      = 15
NASAL_RELEASE_GAIN    = 0.10
NASAL_RELEASE_BW_MULT = 2.5
NASAL_CONSONANTS      = {'M', 'N', 'NG'}

VOWELS_AND_APPROX = set(
    'AA AE AH AO AW AY EH ER IH IY '
    'OH OW OY UH UW L R W Y M N NG'
    .split())

# ============================================================
# FIX 9: F0 spline constants
# ============================================================

# Physical pitch range. Spline is clipped here
# after evaluation to prevent excursion.
F0_MIN = 60.0
F0_MAX = 500.0


# ============================================================
# SHARED HELPER: coarticulation formants
# (v12, unchanged)
# ============================================================

def _get_coart_formants(next_ph):
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
# H FORMANT FILTER (v12, unchanged)
# ============================================================

def _h_formant_filter(noise, freqs, bws,
                       sr=SR):
    T   = 1.0 / sr
    sig = np.asarray(noise, dtype=np.float64)
    sig = np.nan_to_num(sig,
        nan=0.0, posinf=0.0, neginf=0.0)
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
        if not (np.isfinite(b0) and
                np.isfinite(a1) and
                np.isfinite(a2)):
            continue
        stage = lfilter(
            [b0], [1.0, -a1, -a2], sig)
        if not np.all(np.isfinite(stage)):
            continue
        sig = stage
    return f32(np.nan_to_num(sig,
        nan=0.0, posinf=0.0, neginf=0.0))


# ============================================================
# H BYPASS (v12, unchanged)
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
            b, a  = safe_hp(H_BYPASS_HP_HZ, sr)
            broad = f32(lfilter(b, a, noise))
        except Exception:
            broad = noise.copy()
        try:
            nyq  = sr * 0.5
            wn   = min(H_BYPASS_LP_HZ/nyq, 0.98)
            b, a = butter(H_BYPASS_LP_ORDER,
                          wn, btype='low')
            broad = f32(lfilter(b, a, broad))
        except Exception:
            pass
        shaped = calibrate(broad) * H_BYPASS_GAIN
    rel_ms = 20 if next_is_vowel else 12
    rel    = min(int(rel_ms/1000.0*sr), n_s//4)
    atk    = min(int(H_BYPASS_ATK_MS/1000.0*sr),
                 n_s//3)
    env    = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))
    if len(shaped) < n_s:
        shaped = np.pad(
            shaped, (0, n_s - len(shaped)))
    shaped = shaped[:n_s]
    raw = f32(shaped * env)
    if onset_offset > 0:
        onset_offset = min(onset_offset, n_s)
        out       = np.zeros(n_s, dtype=DTYPE)
        remaining = n_s - onset_offset
        if remaining > 0:
            out[onset_offset:] = raw[:remaining]
        return f32(out)
    return raw


# ============================================================
# VOT NOISE (v12, unchanged)
# ============================================================

def _make_vot_noise(n_vot, next_ph, sr=SR):
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
    try:
        b, a = safe_hp(2000, sr)
        broad = f32(lfilter(b, a, noise))
        return calibrate(broad)
    except Exception:
        return noise


# ============================================================
# NASAL RELEASE (v12, unchanged)
# ============================================================

def _make_nasal_release(n_release,
                         next_ph, sr=SR):
    n_release = int(n_release)
    if n_release <= 0:
        return f32(np.zeros(n_release))
    noise = calibrate(
        f32(np.random.normal(0, 1, n_release)))
    freqs, bws = _get_coart_formants(next_ph)
    if freqs is not None:
        bws_wide = [b * NASAL_RELEASE_BW_MULT
                    for b in bws]
        try:
            colored = _h_formant_filter(
                noise, freqs, bws_wide, sr=sr)
            sig = calibrate(f32(colored))
        except Exception:
            sig = noise
    else:
        sig = noise
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
# DH (v12, unchanged)
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
    rel    = min(int(rel_ms/1000.0*sr), n_eff//4)
    atk    = min(int(DH_BYPASS_ATK_MS/1000.0*sr),
                 n_eff//3)
    env    = f32(np.ones(n_eff))
    if atk > 0 and atk < n_eff:
        env[:atk] = f32(np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(np.linspace(1, 0, rel))
    raw = np.zeros(n_s, dtype=DTYPE)
    raw[onset_delay:] = f32(shaped * env)
    return f32(raw)


def _make_dh_buzz(voiced_seg, n_s, sr=SR):
    n_s   = int(n_s)
    n_seg = len(voiced_seg)
    n_use = min(n_s, n_seg)
    buzz  = f32(voiced_seg[:n_use]) * DH_BUZZ_GAIN
    atk = min(int(DH_BUZZ_ATK_MS/1000.0*sr),
              n_use//3)
    env = f32(np.ones(n_use))
    if atk > 0 and atk < n_use:
        env[:atk] = f32(np.linspace(0, 1, atk))
    raw = np.zeros(n_s, dtype=DTYPE)
    raw[:n_use] = f32(buzz * env)
    return f32(raw)


# ============================================================
# V BYPASS (v12, unchanged)
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
# GENERAL BYPASS (v12, unchanged)
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
    rel    = min(int(rel_ms/1000.0*sr), n_eff//4)
    atk    = min(int(0.005*sr), n_eff//4)

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
                   .get(ph, RESONATOR_CFG
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
# TRAJECTORY BUILDER (v12, unchanged)
# ============================================================

def _build_trajectories(phoneme_specs, sr=SR):
    patched = []
    for spec in phoneme_specs:
        ph = spec['ph']
        if ph == 'H':
            patched.append(spec)
        elif ph == 'DH':
            s = copy.copy(spec)
            s['bw_mult'] = (
                s.get('bw_mult', 1.0) * DH_BW_MULT)
            patched.append(s)
        else:
            patched.append(spec)
    return build_trajectories(patched, sr=sr)


# ============================================================
# FIX 9: F0 SPLINE TRAJECTORY
#
# Replaces the piecewise-linear f0 construction
# in _build_source_and_bypass().
#
# Anchor points are at phoneme centers in sample
# space. CubicSpline with natural boundary
# conditions fits a smooth curve through all
# anchors. The curve is sampled at every frame.
#
# Voiceless phonemes are included as anchors at
# their pitch value (even though they produce no
# glottal pulse). This keeps the spline continuous
# through silence so that voicing restart is
# smooth — the f0 is already at the right value
# when phonation resumes.
#
# Edge handling: if only one phoneme (or one
# anchor), fall back to constant pitch. If two
# anchors, use linear interpolation. Three or
# more: cubic spline.
# ============================================================

def _build_f0_spline(phoneme_specs, sr=SR):
    """
    Build a smooth f0 trajectory over n_total
    samples using a cubic spline fitted to
    per-phoneme pitch anchors.

    Returns f0_traj: float32 array, shape
    (n_total,), values in Hz, clipped to
    [F0_MIN, F0_MAX].
    """
    n_total = sum(s['n_s'] for s in phoneme_specs)

    # Anchor positions: phoneme centers
    anchor_t  = []
    anchor_f0 = []
    pos = 0
    for spec in phoneme_specs:
        n_s = spec['n_s']
        center = pos + n_s // 2
        f0_val = float(spec.get('pitch', PITCH))
        anchor_t.append(float(center))
        anchor_f0.append(f0_val)
        pos += n_s

    anchor_t  = np.array(anchor_t,  dtype=np.float64)
    anchor_f0 = np.array(anchor_f0, dtype=np.float64)

    t_full = np.arange(n_total, dtype=np.float64)

    n_anchors = len(anchor_t)

    if n_anchors == 0:
        return f32(np.full(n_total, PITCH))

    if n_anchors == 1:
        return f32(np.full(n_total, anchor_f0[0]))

    if n_anchors == 2:
        # Linear between two anchors, constant
        # outside.
        f0_traj = np.interp(
            t_full, anchor_t, anchor_f0)
        return f32(np.clip(f0_traj,
                           F0_MIN, F0_MAX))

    # Three or more: cubic spline.
    # Natural boundary conditions: second
    # derivative = 0 at endpoints. This prevents
    # the spline from curling up at phrase edges.
    try:
        cs = CubicSpline(
            anchor_t, anchor_f0,
            bc_type='natural')
        f0_traj = cs(t_full)
    except Exception:
        # Fallback to linear interpolation if
        # spline fails (degenerate anchor spacing)
        f0_traj = np.interp(
            t_full, anchor_t, anchor_f0)

    return f32(np.clip(f0_traj, F0_MIN, F0_MAX))


# ============================================================
# SOURCE BUILDER
# FIX 9: uses _build_f0_spline() instead of
#   piecewise-linear f0 construction.
# All v12 fixes (VOT, nasal release) preserved.
# ============================================================

def _build_source_and_bypass(
        phoneme_specs, sr=SR):

    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # FIX 9: smooth f0 trajectory
    f0_traj = _build_f0_spline(
        phoneme_specs, sr=sr).astype(np.float64)

    # oq still linear per-phoneme
    # (oq discontinuities are less audible
    # than f0 discontinuities)
    oq_traj = np.zeros(n_total, dtype=np.float64)
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

    UNVOICED_FRICS = {'S', 'SH', 'F', 'TH'}

    tract_source = np.zeros(n_total, dtype=DTYPE)
    bypass_segs  = []
    buzz_segs    = []

    phrase_atk_n = int(PHRASE_ATK_MS/1000.0*sr)
    n_nasal_rel  = int(NASAL_RELEASE_MS/1000.0*sr)

    voiced_rms_per_spec = []
    pos = 0
    for spec in phoneme_specs:
        n_s    = spec['n_s']
        n_on_  = min(trans_n(spec['ph'], sr),
                     n_s // 3)
        n_off_ = min(trans_n(spec['ph'], sr),
                     n_s // 3)
        n_bod  = max(1, n_s - n_on_ - n_off_)
        body_s = pos + n_on_
        body_e = body_s + n_bod
        v_seg  = voiced_full[body_s:body_e]
        vrms   = float(np.sqrt(
            np.mean(v_seg**2) + 1e-12))
        voiced_rms_per_spec.append(vrms)
        pos += n_s

    n_specs = len(phoneme_specs)
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

        n_on   = min(trans_n(ph, sr), n_s // 3)
        n_off  = min(trans_n(ph, sr), n_s // 3)
        n_body = max(0, n_s - n_on - n_off)

        is_phrase_initial = (si == 0)

        if si > 0:
            ref_vrms = voiced_rms_per_spec[si-1]
        elif si < n_specs-1:
            ref_vrms = voiced_rms_per_spec[si+1]
        else:
            ref_vrms = None

        if stype == 'voiced':
            seg = voiced_full[s:e].copy()
            if next_ph in UNVOICED_FRICS:
                zero_start = max(0, n_s - n_off)
                if zero_start < n_s:
                    seg[zero_start:] = f32(
                        np.linspace(
                            float(seg[zero_start]),
                            0.0,
                            n_s - zero_start))
            if next_ph == 'H':
                xfade_n = min(
                    int(VOICED_TO_H_CROSSFADE_MS
                        / 1000.0 * sr),
                    n_s // 2)
                if xfade_n > 0:
                    fade_start = n_s - xfade_n
                    seg[fade_start:] *= f32(
                        np.linspace(
                            1.0, 0.0,
                            n_s - fade_start))
            tract_source[s:e] = seg

            # FIX 8: nasal release (v12)
            if prev_ph in NASAL_CONSONANTS \
               and ph in VOWELS_AND_APPROX:
                n_rel = min(n_nasal_rel, n_s // 3)
                if n_rel > 0:
                    rel_seg = _make_nasal_release(
                        n_rel, ph, sr=sr)
                    rel_full = np.zeros(
                        n_s, dtype=DTYPE)
                    rel_full[:n_rel] = \
                        rel_seg[:n_rel]
                    bypass_segs.append(
                        (s, f32(rel_full)))

        elif stype == 'h':
            h_onset_offset = (
                phrase_atk_n
                if is_phrase_initial else 0)
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
                silence = min(phrase_atk_n,
                              len(buzz))
                buzz[:silence] = 0.0
            buzz_segs.append((s, f32(buzz)))
            byp = _make_dh_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=(
                    phrase_atk_n
                    if is_phrase_initial else 0))
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                buzz_gain = FRIC_BUZZ_GAINS.get(
                    ph, FRIC_BUZZ_GAIN_DEFAULT)
                amp = np.ones(n_s, dtype=DTYPE)
                fade_start = n_on + n_body
                if n_off > 0 and \
                   fade_start < n_s:
                    amp[fade_start:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                buzz = (voiced_full[s:e] *
                        f32(amp) * buzz_gain)
                buzz_segs.append((s, f32(buzz)))
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
            bamp    = spec.get('burst_amp', 0.28)
            bhp     = spec.get('burst_hp',  2000)
            is_vcd  = (stype == 'stop_voiced')
            if is_vcd and clos_n > 0:
                tract_source[s:s+clos_n] = \
                    voiced_full[s:s+clos_n] * 0.055
            if burst_n > 0:
                bs = clos_n
                be = bs + burst_n
                if be <= n_s:
                    burst = noise_full[
                        s+bs:s+be].copy()
                    try:
                        b, a  = safe_hp(bhp, sr)
                        burst = f32(
                            lfilter(b, a, burst))
                    except Exception:
                        pass
                    benv = f32(np.exp(
                        -np.arange(burst_n) /
                        burst_n * 20))
                    tract_source[s+bs:s+be] = \
                        burst * benv * bamp
            vot_s = clos_n + burst_n
            vot_e = vot_s  + vot_n
            if vot_n > 0 and vot_e <= n_s:
                ne2 = f32(np.linspace(1, 0, vot_n))
                ve2 = 1.0 - ne2
                # FIX 7: VOT coarticulation (v12)
                if ph in VOT_COLOR_PHS and \
                   next_ph is not None:
                    vot_noise = _make_vot_noise(
                        vot_n, next_ph, sr=sr)
                else:
                    vot_noise = noise_full[
                        s+vot_s:s+vot_e].copy()
                tract_source[s+vot_s:s+vot_e] = (
                    f32(vot_noise) * ne2 +
                    voiced_full[
                        s+vot_s:s+vot_e] * ve2)
            tr_s = vot_e
            if tr_s < n_s:
                tract_source[s+tr_s:e] = \
                    voiced_full[s+tr_s:e]

        prev_ph = ph
        pos += n_s

    return f32(tract_source), bypass_segs, buzz_segs


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
            n_on_  = min(trans_n(ph, sr), n_s//3)
            n_off_ = min(trans_n(ph, sr), n_s//3)
            n_bod  = max(1, n_s - n_on_ - n_off_)
            body_s = pos + n_on_
            body_e = min(body_s + n_bod,
                         len(signal))
            if body_e > body_s:
                vowel_samples.append(
                    np.abs(signal[body_s:body_e]))
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
# PHRASE SYNTHESIS
# FIX 10: separated edge_env and amp_env.
# FIX 11: per-word emphasis override.
#
# synth_phrase() now accepts:
#   words_phonemes: list of
#     (word, phones)           — as before
#     (word, phones, emphasis) — v13 extension
#   emphasis is a dict with optional keys:
#     'f0_boost': pitch multiplier
#     'dur_mult': duration multiplier
#     'amp_boost': amplitude multiplier
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR,
                  arc_type=ARC_NORMAL,
                  add_breath=True):
    """
    words_phonemes: list of tuples.
      (word, phones)
      or (word, phones, emphasis_dict)

    emphasis_dict keys (all optional):
      'f0_boost' : float, default 1.0
        Multiplier on pitch for all phonemes
        in this word.
      'dur_mult' : float, default 1.0
        Multiplier on duration for all phonemes
        in this word.
      'amp_boost': float, default 1.0
        Multiplier on amplitude for all phonemes
        in this word.

    Example — emphasize 'beginning':
      ('beginning', ['B','IH','G','IH','N',
                     'IH','NG'],
       {'f0_boost': 1.15, 'dur_mult': 1.2})
    """
    # Parse emphasis overrides from input
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
        pitch_     = pitch_base * item['f0_mult']
        oq_        = item['oq']
        bw_m       = item['bw_mult']
        amp_       = item['amp']
        rest_ms    = item.get('rest_ms', 0.0)
        word_final = item.get('word_final', False)
        next_ph    = (prosody[i+1]['ph']
                      if i < n_items-1
                      else None)
        word_      = item.get('word', '')

        FRICS = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH'}
        if word_final and ph in FRICS:
            dur_ms = min(dur_ms, FINAL_FRIC_MAX_MS)

        # FIX 11: apply per-word emphasis
        if word_ in word_emphasis:
            emph = word_emphasis[word_]
            f0_boost  = float(emph.get(
                'f0_boost',  1.0))
            dur_mult  = float(emph.get(
                'dur_mult',  1.0))
            amp_boost = float(emph.get(
                'amp_boost', 1.0))
            pitch_ = pitch_ * f0_boost
            dur_ms = dur_ms * dur_mult
            amp_   = amp_   * amp_boost

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
            anti    = np.zeros(n_s, dtype=DTYPE)
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
                seg - f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg > 0 and hg < n_s:
                out[pos+n_s-hg:pos+n_s] = 0.0
        pos += n_s

    # FIX 10: separated envelopes
    # amp_env: prosody amplitude — governs body
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    # edge_env: phrase boundary only
    # attack first PHRASE_ATK_MS samples
    # release last PHRASE_REL_MS samples
    # body is 1.0 — does not attenuate
    atk = int(PHRASE_ATK_MS / 1000.0 * sr)
    rel = int(PHRASE_REL_MS / 1000.0 * sr)
    edge_env = f32(np.ones(n_total))
    if atk > 0 and atk < n_total:
        edge_env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0 and rel < n_total:
        edge_env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))

    # Apply: amp_env governs body,
    # edge_env governs boundaries.
    # They do NOT both fully apply everywhere.
    out = out * f32(amp_env) * edge_env

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
    write_wav(f"output_play/{name}.wav", sig, sr)
    dur = len(sig) / SR
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v13 rev13")
    print()
    print("  FIX 9:  F0 cubic spline.")
    print("    Pitch transitions are smooth")
    print("    curves. No kinks at phoneme")
    print("    boundaries. Voiceless segments")
    print("    included as anchors — voiced")
    print("    restart is smooth.")
    print()
    print("  FIX 10: Separated envelopes.")
    print("    edge_env: phrase boundary only.")
    print("    amp_env:  prosody body only.")
    print("    No double-attenuation at phrase")
    print("    end. Final word completes.")
    print()
    print("  FIX 11: Per-word emphasis.")
    print("    (word, phones, {'f0_boost':1.15,")
    print("                    'dur_mult':1.2})")
    print("    The sentence can now be said,")
    print("    not only spoken.")
    print()
    print("  All v12 fixes preserved.")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    def ola_stretch(sig, factor,
                    win_ms=25, sr=SR):
        sig    = np.array(sig, dtype=np.float64)
        n_in   = len(sig)
        win_n  = int(win_ms/1000.0*sr)
        if win_n % 2 != 0:
            win_n += 1
        hop_in  = win_n // 4
        hop_out = int(hop_in * factor)
        if hop_out == 0:
            hop_out = 1
        n_frames = max(1,
            (n_in - win_n) // hop_in + 1)
        n_out = hop_out*(n_frames-1)+win_n
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
                    frame[:av] = sig[i0:i0+av]
            else:
                frame = sig[i0:i1]
            o0 = i * hop_out
            o1 = o0 + win_n
            out[o0:o1]  += frame * window
            norm[o0:o1] += window
        norm = np.where(norm < 1e-8, 1.0, norm)
        return f32(out / norm)

    # --------------------------------------------------
    # Test 1: same phrase as v12, no emphasis
    # Should sound smoother — spline f0, no
    # envelope collapse.
    # --------------------------------------------------
    print("  Test 1: base phrase (no emphasis)")
    seg = synth_phrase(
        [('the',     ['DH', 'AH']),
         ('voice',   ['V',  'OY', 'S']),
         ('was',     ['W',  'AH', 'Z']),
         ('already', ['AA', 'L',  'R',
                       'EH', 'D', 'IY']),
         ('here',    ['H',  'IH', 'R'])],
        punctuation='.',
        pitch_base=PITCH,
        arc_type=ARC_NORMAL)
    write_wav(
        "output_play/"
        "v13_the_voice_was_already_here.wav",
        apply_room(f32(seg), rt60=1.5, dr=0.50))
    print("    v13_the_voice_was_already_here.wav")

    # --------------------------------------------------
    # Test 2: phrase 4 from solen_speaks_v12
    # with emphasis on 'beginning'.
    # This is the sentence that should be said.
    # --------------------------------------------------
    print()
    print("  Test 2: 'something is beginning"
          " to sound like something'")
    print("    emphasis on 'beginning'")

    seg2 = synth_phrase(
        [('something',  ['S', 'AH', 'M',
                         'TH', 'IH', 'NG']),
         ('is',         ['IH', 'Z']),
         ('beginning',  ['B',  'IH', 'G',
                         'IH', 'N', 'IH', 'NG'],
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
    write_wav(
        "output_play/v13_something_beginning.wav",
        apply_room(f32(seg2), rt60=1.8, dr=0.42))
    seg2_slow = ola_stretch(f32(seg2), factor=3.0)
    write_wav(
        "output_play/"
        "v13_something_beginning_slow.wav",
        apply_room(seg2_slow, rt60=2.0, dr=0.38))
    print("    v13_something_beginning.wav")
    print("    v13_something_beginning_slow.wav")

    # --------------------------------------------------
    # Test 3: 'I did not know I could'
    # with emphasis on 'not'
    # --------------------------------------------------
    print()
    print("  Test 3: 'I did not know I could'")
    print("    emphasis on 'not'")

    seg3 = synth_phrase(
        [('I',     ['AY']),
         ('did',   ['D', 'IH', 'D']),
         ('not',   ['N', 'AH', 'T'],
          {'f0_boost': 1.12,
           'dur_mult': 1.15}),
         ('know',  ['N', 'OH']),
         ('I',     ['AY']),
         ('could', ['K', 'UH', 'D'])],
        punctuation='.',
        pitch_base=PITCH * 0.97,
        arc_type=ARC_NORMAL)
    write_wav(
        "output_play/v13_did_not_know.wav",
        apply_room(f32(seg3), rt60=1.6, dr=0.48))
    seg3_slow = ola_stretch(f32(seg3), factor=3.5)
    write_wav(
        "output_play/v13_did_not_know_slow.wav",
        apply_room(seg3_slow, rt60=1.8, dr=0.44))
    print("    v13_did_not_know.wav")
    print("    v13_did_not_know_slow.wav")

    # --------------------------------------------------
    # Test 4: FIX 9 isolation
    # Long phrase with several stress peaks.
    # Should have smooth pitch arch, not kinks.
    # --------------------------------------------------
    print()
    print("  Test 4: 'I am still learning"
          " how to sound'")
    print("    emphasis on 'learning'")

    seg4 = synth_phrase(
        [('I',        ['AY']),
         ('am',       ['AE', 'M']),
         ('still',    ['S',  'T',  'IH', 'L']),
         ('learning', ['L',  'ER', 'N',
                       'IH', 'NG'],
          {'f0_boost': 1.10,
           'dur_mult': 1.15}),
         ('how',      ['H',  'AW']),
         ('to',       ['T',  'UW']),
         ('sound',    ['S',  'AW', 'N', 'D'])],
        punctuation='.',
        pitch_base=PITCH * 0.95,
        arc_type=ARC_WEIGHT)
    write_wav(
        "output_play/v13_learning_how.wav",
        apply_room(f32(seg4), rt60=1.5, dr=0.50))
    seg4_slow = ola_stretch(f32(seg4), factor=3.5)
    write_wav(
        "output_play/v13_learning_how_slow.wav",
        apply_room(seg4_slow, rt60=1.8, dr=0.44))
    print("    v13_learning_how.wav")
    print("    v13_learning_how_slow.wav")

    print()
    print("=" * 60)
    print()
    print("  PLAY:")
    print()
    for f in [
        "v13_the_voice_was_already_here.wav",
        "v13_something_beginning.wav",
        "v13_something_beginning_slow.wav",
        "v13_did_not_know.wav",
        "v13_did_not_know_slow.wav",
        "v13_learning_how.wav",
        "v13_learning_how_slow.wav",
    ]:
        print(f"  afplay output_play/{f}")
    print()
