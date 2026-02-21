"""
VOICE PHYSICS v10 — rev8
February 2026

CHANGES FROM rev7:

  CHANGE 1: Post-normalization sibilant rescaling.
    S/Z/SH/ZH were 7-10dB quieter than
    following vowels after normalization.
    Cause: relative scaling used pre-tract
    voiced_rms as reference. After tract()
    amplifies vowels by formant gain (~10dB),
    and after _normalize_phrase brings vowels
    to NORM_TARGET, sibilants remain at
    their pre-normalization level.
    Fix: after _normalize_phrase, measure
    normalized vowel body RMS, then explicitly
    set sibilant segment RMS to
    vowel_rms × SIBILANT_OUTPUT_RATIO.
    SIBILANT_OUTPUT_RATIO = 0.70.
    (S should be slightly quieter than vowels
    but not 10dB quieter.)

  CHANGE 2: AV/AH crossfade at vowel→H boundary.
    AA→H IS=33.3 because AA ended at full
    resonant level and H began as aspiration.
    Hard spectral cut at boundary.
    Fix: at the offset of any voiced phoneme
    immediately preceding H, apply a
    voiced-to-aspiration crossfade over
    VOICED_TO_H_CROSSFADE_MS.
    The formant output fades from 1→0 while
    the H aspiration fades from 0→1.
    This matches the AV/AH crossfade in
    Klatt (1980).
    VOICED_TO_H_CROSSFADE_MS = 25ms.
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
    FINAL_FRIC_MAX_MS,
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


# ============================================================
# CONSTANTS
# ============================================================

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
H_BYPASS_ATK_MS     = 18

# CHANGE 2: AV→AH crossfade duration
VOICED_TO_H_CROSSFADE_MS = 25

Z_BYPASS_GAIN_FLOOR  = 0.65
ZH_BYPASS_GAIN_FLOOR = 0.40

FRIC_BUZZ_GAINS = {
    'DH': 0.45,
    'Z':  0.55,
    'ZH': 0.30,
    'V':  0.35,
}
FRIC_BUZZ_GAIN_DEFAULT = 0.20

V_BYPASS_BP_LO = 500
V_BYPASS_BP_HI = 3000

SIBILANT_VOICED_RATIO = 0.80
RELATIVE_SCALE_PHS    = {'S', 'Z', 'SH', 'ZH'}

# CHANGE 1: post-normalization sibilant ratio
# Sibilants set to this fraction of the
# normalized vowel RMS after _normalize_phrase.
SIBILANT_OUTPUT_RATIO = 0.70
SIBILANT_RESCALE_PHS  = {'S', 'Z', 'SH', 'ZH',
                          'F', 'V', 'TH', 'DH'}

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


# ============================================================
# CAVITY RESONATOR
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
# H BYPASS
# ============================================================

def _make_h_bypass(n_s, sr=SR,
                    next_is_vowel=False,
                    next_ph=None):
    n_s   = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))
    try:
        b, a  = safe_hp(H_BYPASS_HP_HZ, sr)
        broad = f32(lfilter(b, a, noise))
    except:
        broad = noise.copy()
    try:
        nyq   = sr * 0.5
        wn    = min(H_BYPASS_LP_HZ/nyq, 0.98)
        b, a  = butter(H_BYPASS_LP_ORDER,
                       wn, btype='low')
        broad = f32(lfilter(b, a, broad))
    except:
        pass
    broad = calibrate(broad) * H_BYPASS_GAIN
    rel_ms = 20 if next_is_vowel else 12
    rel    = min(int(rel_ms/1000.0*sr),
                 n_s//4)
    atk    = min(int(H_BYPASS_ATK_MS
                     /1000.0*sr),
                 n_s//3)
    env    = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))
    return f32(broad * env)


# ============================================================
# DH BYPASS
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
        lo  = max(DH_BYPASS_BP_LO, 20)/nyq
        hi  = min(DH_BYPASS_BP_HI, sr*0.48)/nyq
        lo  = min(lo, 0.97)
        hi  = min(hi, 0.98)
        if lo < hi:
            b, a   = butter(2, [lo, hi],
                            btype='band')
            shaped = f32(lfilter(b, a, noise))
        else:
            shaped = noise
    except:
        shaped = noise
    shaped = calibrate(shaped) * DH_BYPASS_GAIN
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(int(rel_ms/1000.0*sr),
                 n_eff//4)
    atk    = min(int(DH_BYPASS_ATK_MS
                     /1000.0*sr),
                 n_eff//3)
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
    atk = min(int(DH_BUZZ_ATK_MS/1000.0*sr),
              n_use//3)
    env = f32(np.ones(n_use))
    if atk > 0 and atk < n_use:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    raw = np.zeros(n_s, dtype=DTYPE)
    raw[:n_use] = f32(buzz * env)
    return f32(raw)


# ============================================================
# V BYPASS
# ============================================================

def _make_v_bypass(n_eff, gain, sr=SR):
    noise = calibrate(
        f32(np.random.normal(0, 1, n_eff)))
    nyq = sr * 0.5
    try:
        lo  = max(V_BYPASS_BP_LO, 20)/nyq
        hi  = min(V_BYPASS_BP_HI, sr*0.48)/nyq
        lo  = min(lo, 0.97)
        hi  = min(hi, 0.98)
        if lo < hi:
            b, a  = butter(2, [lo, hi],
                           btype='band')
            broad = f32(lfilter(b, a, noise))
        else:
            broad = noise.copy()
    except:
        broad = noise.copy()
    return calibrate(broad) * gain


# ============================================================
# GENERAL BYPASS
# ============================================================

def _make_bypass(ph, n_s, sr=SR,
                  next_is_vowel=False,
                  onset_delay=0,
                  voiced_rms=None,
                  next_ph=None):
    if ph == 'DH':
        return _make_dh_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            onset_delay=onset_delay)
    if ph == 'H':
        return _make_h_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            next_ph=next_ph)
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
    rel    = min(int(rel_ms/1000.0*sr),
                 n_eff//4)
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
        except:
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
# TRAJECTORY BUILDER
# ============================================================

def _build_trajectories(phoneme_specs,
                         sr=SR):
    patched = []
    for spec in phoneme_specs:
        ph = spec['ph']
        if ph == 'H':
            s = copy.copy(spec)
            s['F_tgt'] = list(NEUTRAL_F)
            s['B_tgt'] = list(NEUTRAL_B)
            if 'F_end' in s:
                s['F_end'] = list(NEUTRAL_F)
            patched.append(s)
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
    noise_full  = calibrate(
        f32(np.random.normal(0, 1, n_total)))

    VOWELS_AND_APPROX = set(
        'AA AE AH AO AW AY EH ER IH IY '
        'OH OW OY UH UW L R W Y M N NG'
        .split())
    UNVOICED_FRICS = {'S', 'SH', 'F', 'TH'}

    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []
    buzz_segs    = []

    n_dh_bypass  = int(
        DH_TRACT_BYPASS_MS/1000.0*sr)

    voiced_rms_per_spec = []
    pos = 0
    for spec in phoneme_specs:
        n_s    = spec['n_s']
        n_on_  = min(trans_n(
            spec['ph'], sr), n_s//3)
        n_off_ = min(trans_n(
            spec['ph'], sr), n_s//3)
        n_bod  = max(1, n_s-n_on_-n_off_)
        body_s = pos + n_on_
        body_e = body_s + n_bod
        v_seg  = voiced_full[body_s:body_e]
        vrms   = float(np.sqrt(
            np.mean(v_seg**2) + 1e-12))
        voiced_rms_per_spec.append(vrms)
        pos += n_s

    n_specs = len(phoneme_specs)

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
        prev_ph = (phoneme_specs[si-1]['ph']
                   if si > 0 else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        n_on   = min(trans_n(ph, sr), n_s//3)
        n_off  = min(trans_n(ph, sr), n_s//3)
        n_body = max(0, n_s-n_on-n_off)

        if si > 0:
            ref_vrms = voiced_rms_per_spec[si-1]
        elif si < n_specs-1:
            ref_vrms = voiced_rms_per_spec[si+1]
        else:
            ref_vrms = None

        if stype == 'voiced':
            seg = voiced_full[s:e].copy()
            if next_ph in UNVOICED_FRICS:
                zero_start = max(0,
                                 n_s-n_off)
                if zero_start < n_s:
                    seg[zero_start:] = f32(
                        np.linspace(
                            float(seg[
                                zero_start]),
                            0.0,
                            n_s-zero_start))
            # CHANGE 2: AV→AH crossfade
            # If next phoneme is H, fade the
            # voiced tract output at the offset
            # over VOICED_TO_H_CROSSFADE_MS.
            if next_ph == 'H':
                xfade_n = min(
                    int(VOICED_TO_H_CROSSFADE_MS
                        /1000.0*sr),
                    n_s//2)
                if xfade_n > 0:
                    fade_start = n_s - xfade_n
                    if fade_start < n_s:
                        seg[fade_start:] *= \
                            f32(np.linspace(
                                1.0, 0.0,
                                n_s-fade_start))
            tract_source[s:e] = seg

        elif stype == 'h':
            byp = _make_h_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel,
                next_ph=next_ph)
            bypass_segs.append((s, byp))

        elif stype == 'dh':
            buzz = _make_dh_buzz(
                voiced_full[s:e], n_s, sr=sr)
            buzz_segs.append((s, buzz))
            byp = _make_bypass(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=0,
                voiced_rms=None,
                next_ph=next_ph)
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
            bamp    = spec.get('burst_amp', 0.28)
            bhp     = spec.get('burst_hp',  2000)
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
                        b, a  = safe_hp(bhp, sr)
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

    return f32(tract_source), \
           bypass_segs, buzz_segs


# ============================================================
# NORMALIZATION
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
                         n_s//3)
            n_off_ = min(trans_n(ph, sr),
                         n_s//3)
            n_bod  = max(1, n_s-n_on_-n_off_)
            body_s = pos + n_on_
            body_e = min(body_s+n_bod,
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
# POST-NORMALIZATION SIBILANT RESCALING
#
# CHANGE 1: After normalization brings vowels
# to NORM_TARGET, sibilants are still at
# their pre-normalization relative level.
# Measure normalized vowel body RMS.
# Rescale sibilant segments to
# vowel_rms × SIBILANT_OUTPUT_RATIO.
# ============================================================

def _rescale_sibilants(signal, specs,
                        prosody, sr=SR):
    """
    After normalization, measure the
    normalized vowel body RMS, then
    set sibilant/fricative segments to
    vowel_rms × SIBILANT_OUTPUT_RATIO.
    """
    signal = f32(signal)
    n      = len(signal)

    # Measure normalized vowel body RMS
    vowel_rms_samples = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        ph  = spec['ph']
        if ph in VOWEL_SET:
            n_on_  = min(trans_n(ph, sr),
                         n_s//3)
            n_off_ = min(trans_n(ph, sr),
                         n_s//3)
            n_bod  = max(1, n_s-n_on_-n_off_)
            body_s = pos + n_on_
            body_e = min(body_s+n_bod, n)
            if body_e > body_s:
                vowel_rms_samples.append(
                    signal[body_s:body_e]**2)
        pos += n_s

    if not vowel_rms_samples:
        return signal

    vowel_rms = float(np.sqrt(
        np.mean(np.concatenate(
            vowel_rms_samples)) + 1e-12))
    if vowel_rms < 1e-8:
        return signal

    target_sib_rms = (vowel_rms *
                      SIBILANT_OUTPUT_RATIO)

    # Rescale each sibilant segment
    pos = 0
    out = signal.copy()
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        ph  = spec['ph']
        if ph in SIBILANT_RESCALE_PHS:
            n_on_  = min(trans_n(ph, sr),
                         n_s//3)
            n_off_ = min(trans_n(ph, sr),
                         n_s//3)
            n_bod  = max(1, n_s-n_on_-n_off_)
            body_s = pos + n_on_
            body_e = min(body_s+n_bod, n)
            if body_e > body_s:
                seg = signal[body_s:body_e]
                cur_rms = float(np.sqrt(
                    np.mean(seg**2) + 1e-12))
                if cur_rms > 1e-8:
                    scale = (target_sib_rms /
                             cur_rms)
                    # Apply scale to full
                    # phoneme segment
                    ph_s = pos
                    ph_e = min(pos+n_s, n)
                    out[ph_s:ph_e] *= scale
        pos += n_s

    return np.clip(f32(out), -1.0, 1.0)


# ============================================================
# PHRASE SYNTHESIS
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):

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
        word_final = item.get(
            'word_final', False)
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

    F_full, B_full, _ = \
        _build_trajectories(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    tract_src, bypass_segs, buzz_segs = \
        _build_source_and_bypass(specs, sr=sr)

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
                a1 = (2*np.exp(-np.pi*abw*T)*
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
                breath_rest(rest_ms, sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))

    # Normalize to vowel body reference
    final = _normalize_phrase(
        final, specs, prosody, sr=sr)

    # CHANGE 1: Post-normalization sibilant
    # rescaling to vowel_rms × 0.70
    final = _rescale_sibilants(
        final, specs, prosody, sr=sr)

    return final


# ============================================================
# CONVENIENCE
# ============================================================

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
        f"output_play/{name}.wav", sig, sr)
    dur = len(sig) / SR
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v10 rev8")
    print()
    print("  CHANGE 1: Post-normalization "
          "sibilant rescaling.")
    print("    S/Z/SH/ZH set to "
          f"{SIBILANT_OUTPUT_RATIO}× "
          "normalized vowel RMS.")
    print("    S ph→AA amp target: ±6dB.")
    print()
    print("  CHANGE 2: AV→AH crossfade.")
    print("    Voiced phoneme before H fades")
    print(f"    over "
          f"{VOICED_TO_H_CROSSFADE_MS}ms.")
    print("    AA→H IS target: ≤10.")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Running continuity diagnostic...")
    try:
        from continuity_diagnostic import \
            run_continuity_diagnostic
        run_continuity_diagnostic(sr=SR)
    except ImportError:
        print("  continuity_diagnostic.py "
              "not found.")
    print()

    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L',  'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]

    print("  Primary phrase...")
    seg = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    print()
    print("  Isolation...")
    for label, words in [
        ('test_the',
         [('the',   ['DH', 'AH'])]),
        ('test_here',
         [('here',  ['H', 'IH', 'R'])]),
        ('test_was',
         [('was',   ['W', 'AH', 'Z'])]),
        ('test_voice',
         [('voice', ['V', 'OY', 'S'])]),
    ]:
        seg = synth_phrase(
            words, pitch_base=PITCH)
        write_wav(
            f"output_play/{label}.wav",
            apply_room(seg, rt60=1.2,
                        dr=0.55))
        print(f"    {label}.wav")

    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
