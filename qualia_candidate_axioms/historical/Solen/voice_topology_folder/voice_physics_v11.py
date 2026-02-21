"""
VOICE PHYSICS v11 — rev11
February 2026

CHANGES FROM rev10:

  FIX 1: Phrase-attack artifact on H and DH.
    (preserved from rev10)

  FIX 2: Z buzz too quiet.
    (preserved from rev10)

  FIX 3: V sounds like static buzz.
    (preserved from rev10)

  FIX 4: S too long in word-final position.
    (preserved from rev10)

  FIX 5: H uses generic broadband noise.
    H was generating noise filtered through
    a fixed HP/LP pair (200Hz–1500Hz)
    regardless of the following phoneme.
    next_ph was accepted as a parameter
    but never used.
    Physical truth: H = voiceless airflow
    through the CURRENT tract configuration,
    which is already shaped for the following
    phoneme before H begins.
    Fix A: _make_h_bypass() now filters noise
    through the following phoneme's formant
    values from VOWEL_F.
    Fix B: _build_trajectories() no longer
    forces H to NEUTRAL_F. H passes through
    with the correct target formants so the
    tract is in the right configuration
    during the bypass.
    Result: H in 'hear' has IH spectral shape.
            H in 'have' has AE spectral shape.
            H in 'hmmm' has M/nasal shape.
    One algorithm. The tract is the variable.
    H is the constant.
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

VOICE_VERSION = 'v11-rev11'

# ============================================================
# CONSTANTS
# ============================================================

PHRASE_ATK_MS       = 25   # phrase onset ramp

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
H_BYPASS_ATK_MS     = 30   # FIX 1: was 18

# FIX 5: H unified model constants
# H filters noise through following phoneme's
# formant configuration.
H_USE_NEXT_FORMANTS = True

# Nasal phonemes: when H precedes M, N, NG
# use nasal tract formant profile.
# Nasal pole ~250Hz, anti-resonance ~750Hz.
H_NASAL_FORMANTS = [250,  1000, 2200, 3300, 4000]
H_NASAL_BW       = [80,   150,  200,  250,  300]
H_NASAL_PHS      = {'M', 'N', 'NG'}

# Stop phonemes: H before stops uses neutral
# fallback. Stop closure has no stable tract
# configuration to preview.
H_STOP_PHS = {'P', 'B', 'T', 'D', 'K', 'G',
               'CH', 'JH'}

# FIX 2: Z buzz louder, bypass floor lower
Z_BYPASS_GAIN_FLOOR  = 0.35   # was 0.65
ZH_BYPASS_GAIN_FLOOR = 0.40

FRIC_BUZZ_GAINS = {
    'DH': 0.45,
    'Z':  1.20,   # FIX 2: was 0.55
    'ZH': 0.30,
    'V':  0.25,   # FIX 3: was 0.35
}
FRIC_BUZZ_GAIN_DEFAULT = 0.20

# FIX 3: V narrower bandpass
V_BYPASS_BP_LO = 800    # was 500
V_BYPASS_BP_HI = 2200   # was 3000

# FIX 4: word-final fricative cap
FINAL_FRIC_MAX_MS = 100  # was effectively 180

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
# H BYPASS — FIX 5: UNIFIED MODEL
# H = voiceless airflow through current
# vocal tract configuration.
# The tract is already shaped for the
# following phoneme when H begins.
# ============================================================

def _make_h_bypass(n_s, sr=SR,
                    next_is_vowel=False,
                    next_ph=None,
                    onset_offset=0):
    """
    H UNIFIED MODEL (FIX 5).

    H = voiceless airflow through current
    vocal tract configuration.

    If next_ph is a vowel/sonorant:
      Filter noise through that phoneme's
      formant values from VOWEL_F.
      H in 'hear' gets IH formants.
      H in 'have' gets AE formants.

    If next_ph is a nasal (M, N, NG):
      Filter noise through nasal tract
      formant profile.
      H in 'hmmm' gets nasal pole ~250Hz.

    If next_ph is a stop or unknown:
      Fall back to original HP/LP broadband.
      Safe behavior for all edge cases.

    onset_offset: samples of silence before
    bypass starts. Phrase-initial H fix
    from rev10, fully preserved.
    """
    n_s   = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))

    # --- DETERMINE FORMANTS FOR H ---
    # H takes the formants of the following
    # phoneme. The tract is already there.
    shaped = None

    if H_USE_NEXT_FORMANTS and \
       next_ph is not None and \
       next_ph not in H_STOP_PHS:

        if next_ph in H_NASAL_PHS:
            # Nasal following phoneme:
            # use nasal tract formants.
            freqs = H_NASAL_FORMANTS
            bws   = H_NASAL_BW
            try:
                # Filter noise through
                # nasal formants using
                # cascade of resonators.
                T   = 1.0 / sr
                sig = noise.copy()
                for fc, bw in zip(freqs, bws):
                    a2 = -np.exp(
                        -2*np.pi*bw*T)
                    a1 = (2*np.exp(
                        -np.pi*bw*T) *
                        np.cos(2*np.pi*fc*T))
                    b0 = 1.0 - a1 - a2
                    y1 = y2 = 0.0
                    out = np.zeros(
                        len(sig), dtype=DTYPE)
                    for i in range(len(sig)):
                        y = (b0*float(sig[i])
                             + a1*y1 + a2*y2)
                        y2 = y1
                        y1 = y
                        out[i] = y
                    sig = f32(out)
                shaped = (calibrate(sig)
                          * H_BYPASS_GAIN)
            except Exception:
                shaped = None

        elif next_ph in VOWEL_F:
            # Oral vowel or sonorant:
            # use that phoneme's formants.
            try:
                freqs = list(VOWEL_F[next_ph])
                try:
                    bws = [get_b(next_ph, i)
                           for i in range(
                               len(freqs))]
                except Exception:
                    bws = [80, 90, 120,
                           150, 200
                           ][:len(freqs)]

                T   = 1.0 / sr
                sig = noise.copy()
                for fc, bw in zip(freqs, bws):
                    fc = float(fc)
                    bw = float(bw)
                    if fc <= 0 or bw <= 0:
                        continue
                    a2 = -np.exp(
                        -2*np.pi*bw*T)
                    a1 = (2*np.exp(
                        -np.pi*bw*T) *
                        np.cos(2*np.pi*fc*T))
                    b0 = 1.0 - a1 - a2
                    y1 = y2 = 0.0
                    out = np.zeros(
                        len(sig), dtype=DTYPE)
                    for i in range(len(sig)):
                        y = (b0*float(sig[i])
                             + a1*y1 + a2*y2)
                        y2 = y1
                        y1 = y
                        out[i] = y
                    sig = f32(out)
                shaped = (calibrate(sig)
                          * H_BYPASS_GAIN)
            except Exception:
                shaped = None

    # --- FALLBACK: original broadband ---
    # Used when next_ph unknown, is a stop,
    # or formant filtering fails.
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
        shaped = calibrate(broad) * H_BYPASS_GAIN

    # --- ENVELOPE ---
    rel_ms = 20 if next_is_vowel else 12
    rel    = min(int(rel_ms / 1000.0 * sr),
                 n_s // 4)
    atk    = min(int(H_BYPASS_ATK_MS
                     / 1000.0 * sr),
                 n_s // 3)
    env    = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.0, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))

    raw = f32(shaped[:n_s] * env
              if len(shaped) >= n_s
              else np.pad(
                  shaped,
                  (0, n_s - len(shaped)))
              * env)

    # --- ONSET OFFSET (phrase-initial) ---
    # Preserved from FIX 1 in rev10.
    if onset_offset > 0:
        onset_offset = min(onset_offset, n_s)
        out = np.zeros(n_s, dtype=DTYPE)
        remaining = n_s - onset_offset
        if remaining > 0:
            out[onset_offset:] = \
                raw[:remaining]
        return f32(out)
    return raw


# ============================================================
# DH BYPASS + BUZZ
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
        hi  = min(DH_BYPASS_BP_HI,
                  sr*0.48)/nyq
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
# V BYPASS — FIX 3: narrower BP
# ============================================================

def _make_v_bypass(n_eff, gain, sr=SR):
    noise = calibrate(
        f32(np.random.normal(0, 1, n_eff)))
    nyq = sr * 0.5
    try:
        lo  = max(V_BYPASS_BP_LO, 20)/nyq
        hi  = min(V_BYPASS_BP_HI,
                  sr*0.48)/nyq
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
# GENERAL BYPASS
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
# TRAJECTORY BUILDER
# FIX 5: H no longer forced to NEUTRAL_F.
# H passes through with its assigned
# target formants so the tract is in the
# correct configuration during the bypass.
# ============================================================

def _build_trajectories(phoneme_specs,
                         sr=SR):
    patched = []
    for spec in phoneme_specs:
        ph = spec['ph']
        if ph == 'H':
            # FIX 5: do NOT override H to
            # NEUTRAL_F. The tract should be
            # in the following phoneme's
            # configuration — not neutral.
            # Forcing neutral was creating
            # the junction discontinuity.
            # Pass through unchanged.
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
    phrase_atk_n = int(
        PHRASE_ATK_MS/1000.0*sr)

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
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        n_on   = min(trans_n(ph, sr), n_s//3)
        n_off  = min(trans_n(ph, sr), n_s//3)
        n_body = max(0, n_s-n_on-n_off)

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
                zero_start = max(0,
                                 n_s-n_off)
                if zero_start < n_s:
                    seg[zero_start:] = f32(
                        np.linspace(
                            float(seg[
                                zero_start]),
                            0.0,
                            n_s-zero_start))
            if next_ph == 'H':
                xfade_n = min(
                    int(VOICED_TO_H_CROSSFADE_MS
                        /1000.0*sr),
                    n_s//2)
                if xfade_n > 0:
                    fade_start = n_s - xfade_n
                    seg[fade_start:] *= \
                        f32(np.linspace(
                            1.0, 0.0,
                            n_s-fade_start))
            tract_source[s:e] = seg

        elif stype == 'h':
            # FIX 1: phrase-initial H onset
            # offset skips phrase_atk transient
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
            # FIX 1: phrase-initial DH
            # also offset by phrase_atk
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
                    if is_phrase_initial
                    else 0))
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
# PHRASE SYNTHESIS
# FIX 4: word-final fricatives use
# FINAL_FRIC_MAX_MS cap via ph_spec_v9
# word_final flag.
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

        # FIX 4: cap word-final fricatives
        FRICS = {'S','Z','SH','ZH',
                 'F','V','TH','DH'}
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
    final = _normalize_phrase(
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
# MAIN — renders and runs slow diagnostic
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v11 rev11")
    print()
    print("  FIX 1: H/DH phrase-initial "
          "onset offset")
    print("    Phrase-attack artifact suppressed.")
    print("  FIX 2: Z_BUZZ_GAIN=1.20, "
          "Z floor=0.35")
    print("    Z should now sound voiced.")
    print("  FIX 3: V BP(800-2200Hz), "
          "buzz=0.25")
    print("    V more focused labiodental.")
    print("  FIX 4: word-final fric "
          "cap=100ms")
    print("    S in 'voice' shorter.")
    print("  FIX 5: H unified model.")
    print("    H now uses next phoneme's "
          "formants.")
    print("    H in 'hear' → IH spectral shape.")
    print("    H in 'have' → AE spectral shape.")
    print("    H in 'hmmm' → nasal shape.")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L',  'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]

    def ola_stretch(sig, factor,
                    win_ms=25, sr=SR):
        sig   = np.array(sig,
                         dtype=np.float32)
        n_in  = len(sig)
        win_n = int(win_ms/1000.0*sr)
        if win_n % 2 != 0:
            win_n += 1
        hop_in  = win_n // 4
        hop_out = int(hop_in * factor)
        n_frames = max(1,
            (n_in-win_n)//hop_in + 1)
        n_out = hop_out*(n_frames-1)+win_n
        out  = np.zeros(n_out,
                        dtype=np.float64)
        norm = np.zeros(n_out,
                        dtype=np.float64)
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
                frame = sig[i0:i1].astype(
                    np.float64)
            o0 = i * hop_out
            o1 = o0 + win_n
            out[o0:o1]  += frame * window
            norm[o0:o1] += window
        norm = np.where(
            norm < 1e-8, 1.0, norm)
        return (out/norm).astype(np.float32)

    print("  Full phrase (normal speed)...")
    seg = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(f32(seg),
                   rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    print()
    print("  4× OLA slow — word by word...")
    for word, phones in PHRASE:
        sig_w = synth_phrase(
            [(word, phones)],
            pitch_base=PITCH)
        sig_w = ola_stretch(
            f32(sig_w), factor=4.0)
        sig_w = apply_room(
            sig_w, rt60=0.8, dr=0.65)
        write_wav(
            f"output_play/slow_{word}.wav",
            sig_w, SR)
        dur = len(sig_w)/SR
        print(f"    slow_{word}.wav  "
              f"({dur:.1f}s)  {phones}")

    print()
    print("  PLAY:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    for word, _ in PHRASE:
        print(f"  afplay output_play/"
              f"slow_{word}.wav")
