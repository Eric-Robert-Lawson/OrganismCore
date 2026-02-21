"""
VOICE PHYSICS v10 — rev4
February 2026

ARTIFACT: IIR resonator ringing
in phoneme bodies.

Observed:
  S/Z: high-pitched ring during body.
       cavity_resonator Q=22 at 8800Hz.
       Narrow pole rings audibly.
  DH:  low-pitched ring during body.
       tract F1=270Hz with narrow BW.
       Pole rings at F1 frequency.
  H:   low-mid ring during body.
       butter LP(2500Hz, order=2)
       pole at 2500Hz rings briefly.

Root cause: all IIR resonators.
Q too high for consonant annunciation.

Fix:
  S/Z cavity_resonator bw: 400 → 1200Hz
      Q: 22 → 7.3  (no audible ring)
  DH  tract BW multiplier: use wide BW
      bw_mult passed to ph_spec for DH
      increases F1 BW 80 → 200Hz
  H   LP filter: order 2 → order 1
      first-order LP has no poles that ring

All other fixes from rev3 preserved.
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
# v10 rev4 CONSTANTS
# ============================================================

# FIX 1: DH
DH_TRACT_BYPASS_MS  = 25
DH_VOICED_FRACTION  = 0.30
DH_BYPASS_BP_LO     = 1800
DH_BYPASS_BP_HI     = 6500
DH_BYPASS_GAIN      = 0.35
DH_BYPASS_ATK_MS    = 18

# DH tract bandwidth multiplier.
# Widens F1 BW for DH consonant annunciation.
# Prevents F1 resonator from ringing.
# bw_mult=3.0 at F1 BW=80Hz → BW=240Hz.
# Q drops from 3.4 to 1.1. No ring.
DH_BW_MULT          = 3.0

# FIX 2: H
H_BYPASS_HP_HZ      = 200
H_BYPASS_LP_HZ      = 2000  # rev4: was 2500
                             # Lower LP reduces
                             # pole ring frequency.
H_BYPASS_LP_ORDER   = 1     # rev4: was 2.
                             # Order 1 LP has
                             # no resonant pole.
                             # Cannot ring.
H_BYPASS_GAIN       = 0.55
H_BYPASS_ATK_MS     = 18

# FIX 3: Z/ZH gain floors
Z_BYPASS_GAIN_FLOOR  = 0.65
ZH_BYPASS_GAIN_FLOOR = 0.40

# FIX 4: Sibilant bypass relative level
SIBILANT_VOICED_RATIO = 0.80
RELATIVE_SCALE_PHS    = {'S', 'Z', 'SH', 'ZH'}

# FIX 5: Phrase normalization
NORM_PERCENTILE = 90
NORM_TARGET     = 0.88
VOWEL_SET = set(
    'AA AE AH AO AW AY EH ER IH IY '
    'OH OW OY UH UW L R W Y M N NG'
    .split())

# ── rev4: Cavity resonator bandwidths ───────────────────────
#
# Original RESONATOR_CFG (from v9):
#   S:  fc=8800, bw=400  → Q=22  rings audibly
#   Z:  fc=8000, bw=500  → Q=16  rings audibly
#   SH: fc=2500, bw=600  → Q=4.2 marginal
#   ZH: fc=2200, bw=700  → Q=3.1 marginal
#
# rev4 values:
#   S:  fc=8800, bw=1200 → Q=7.3  no audible ring
#   Z:  fc=8000, bw=1200 → Q=6.7  no audible ring
#   SH: fc=2500, bw=900  → Q=2.8  no audible ring
#   ZH: fc=2200, bw=900  → Q=2.4  no audible ring
#
# The wider BW spreads the peak.
# Identity comes from the CENTER frequency,
# not the sharpness of the peak.
# S still sounds like S with Q=7.3.
# The ring at 8800Hz disappears.
#
# F and TH are broadband — no resonator.
# V and DH are also broadband. No change.

RESONATOR_CFG_V10 = {
    'S':  {'fc': 8800, 'bw': 1200,
           'gain': None},
    'Z':  {'fc': 8000, 'bw': 1200,
           'gain': None},
    'SH': {'fc': 2500, 'bw':  900,
           'gain': None},
    'ZH': {'fc': 2200, 'bw':  900,
           'gain': None},
}


# ============================================================
# CAVITY RESONATOR — v10 rev4
# Uses RESONATOR_CFG_V10 bandwidths.
# ============================================================

def _cavity_resonator_v10(noise, ph, sr=SR):
    """
    Apply cavity resonator for phoneme ph.
    Uses wider BW from RESONATOR_CFG_V10.
    Q reduced to eliminate audible ring.
    """
    if ph not in RESONATOR_CFG_V10:
        # Fall back to original
        cfg = RESONATOR_CFG.get(ph, None)
        if cfg is None:
            return noise
        return cavity_resonator(
            noise, cfg['fc'], cfg['bw'], sr=sr)

    cfg = RESONATOR_CFG_V10[ph]
    return cavity_resonator(
        noise, cfg['fc'], cfg['bw'], sr=sr)


# ============================================================
# BYPASS GENERATORS
# ============================================================

def _make_dh_bypass(n_s, sr=SR,
                     next_is_vowel=False,
                     onset_delay=0):
    """
    DH bypass: BP(1800-6500Hz).
    Attack 18ms. No tract resonator.
    """
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
    except:
        shaped = noise

    shaped = calibrate(shaped) * DH_BYPASS_GAIN

    rel_ms = 20 if next_is_vowel else 8
    rel    = min(int(rel_ms / 1000.0 * sr),
                 n_eff // 4)
    atk    = min(int(DH_BYPASS_ATK_MS
                     / 1000.0 * sr),
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


def _make_h_bypass(n_s, sr=SR,
                    next_is_vowel=False):
    """
    H bypass: HP(200Hz) + LP(2000Hz, order=1).
    Order-1 LP has no resonant pole.
    Cannot ring at any frequency.
    Attack 18ms.
    """
    n_s   = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))

    # HP
    try:
        b, a  = safe_hp(H_BYPASS_HP_HZ, sr)
        broad = f32(lfilter(b, a, noise))
    except:
        broad = noise.copy()

    # LP order 1 — no pole ringing
    try:
        nyq   = sr * 0.5
        wn    = min(H_BYPASS_LP_HZ / nyq,
                    0.98)
        b, a  = butter(H_BYPASS_LP_ORDER,
                       wn, btype='low')
        broad = f32(lfilter(b, a, broad))
    except:
        pass

    broad = calibrate(broad) * H_BYPASS_GAIN

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

    return f32(broad * env)


def _make_bypass(ph, n_s, sr=SR,
                  next_is_vowel=False,
                  onset_delay=0,
                  voiced_rms=None):
    """
    General fricative bypass.
    rev4: uses _cavity_resonator_v10
    for S/Z/SH/ZH (wider BW, no ring).
    """
    if ph == 'DH':
        return _make_dh_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            onset_delay=onset_delay)

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
    rel    = min(int(rel_ms / 1000.0 * sr),
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
        # rev4: use wider-BW resonator
        g     = (gain if gain is not None
                 else (RESONATOR_CFG_V10
                       .get(ph, RESONATOR_CFG
                            .get(ph, {}))
                       .get('gain', 0.3)))
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        # Use v10 resonator (wider BW)
        res   = _cavity_resonator_v10(
            noise, ph, sr=sr)
        sib   = calibrate(res)

        if ph in RELATIVE_SCALE_PHS and \
           voiced_rms is not None and \
           voiced_rms > 1e-8:
            sib_rms = float(np.sqrt(
                np.mean(sib**2) + 1e-12))
            if sib_rms > 1e-8:
                target_rms = (voiced_rms *
                    SIBILANT_VOICED_RATIO)
                sib = sib * (target_rms /
                             sib_rms)
        else:
            sib = sib * g

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
                target_rms = (voiced_rms *
                    SIBILANT_VOICED_RATIO)
                sib = sib * (target_rms /
                             sib_rms)
        else:
            sib = sib * g

        raw[onset_delay:] = _env(sib)

    return f32(raw)


# ============================================================
# TRAJECTORY BUILDER v10
# DH uses DH_BW_MULT to widen tract BW.
# Prevents F1 resonator ringing in DH body.
# H uses NEUTRAL_F (tract silent).
# ============================================================

def _build_trajectories(phoneme_specs, sr=SR):
    """
    rev4:
    DH — bandwidth multiplied by DH_BW_MULT.
         Widens F1 from ~80Hz to ~240Hz.
         Q drops from ~3.4 to ~1.1.
         No ring in DH body.
    H  — NEUTRAL_F (tract silent during H).
    """
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
            # Widen all formant bandwidths
            # for DH to damp resonators.
            current_bw = s.get('bw_mult', 1.0)
            s['bw_mult'] = (current_bw *
                            DH_BW_MULT)
            patched.append(s)
        else:
            patched.append(spec)
    return build_trajectories(patched, sr=sr)


# ============================================================
# SOURCE BUILDER v10 rev4
# ============================================================

def _build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v10 rev4: all fixes from rev3 plus:
    - DH bw_mult already applied in
      _build_trajectories.
    - S/Z/SH/ZH use wider cavity resonator
      via _make_bypass → _cavity_resonator_v10.
    - H LP order=1 in _make_h_bypass.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    f0_traj = np.zeros(n_total, dtype=DTYPE)
    oq_traj = np.zeros(n_total, dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s     = spec['n_s']
        f0_this = spec.get('pitch', PITCH)
        oq_this = spec.get('oq', 0.65)
        f0_next = (
            phoneme_specs[si+1]
            .get('pitch', PITCH)
            if si < len(phoneme_specs)-1
            else f0_this)
        oq_next = (
            phoneme_specs[si+1]
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
            (p/oq_) * (2 - p/oq_)
            if p < oq_
            else 1 - (p-oq_) / (1-oq_+1e-9))
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

    tract_source = np.zeros(n_total, dtype=DTYPE)
    bypass_segs  = []
    n_dh_bypass  = int(
        DH_TRACT_BYPASS_MS / 1000.0 * sr)

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

    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source', 'voiced')
        s = pos
        e = pos + n_s

        next_ph = (
            phoneme_specs[si+1]['ph']
            if si < len(phoneme_specs)-1
            else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        n_on   = min(trans_n(ph, sr),
                     n_s // 3)
        n_off  = min(trans_n(ph, sr),
                     n_s // 3)
        n_body = max(0, n_s - n_on - n_off)

        prev_vrms = (
            voiced_rms_per_spec[si-1]
            if si > 0 else None)

        if stype == 'voiced':
            tract_source[s:e] = \
                voiced_full[s:e]

        elif stype == 'h':
            byp = _make_h_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        elif stype == 'dh':
            n_silent = min(n_dh_bypass, n_s)
            n_remain = n_s - n_silent

            voiced_amp = np.zeros(
                n_s, dtype=DTYPE)
            if n_remain > 0:
                voiced_amp[n_silent:] = f32(
                    np.linspace(
                        0.0,
                        DH_VOICED_FRACTION,
                        n_remain))
                fade_start = n_on + n_body
                if n_off > 0 and \
                   fade_start < n_s:
                    v_at_fade = float(
                        voiced_amp[
                            min(fade_start,
                                n_s - 1)])
                    voiced_amp[fade_start:] = \
                        f32(np.linspace(
                            v_at_fade,
                            0.0, n_off))

            tract_source[s:e] = \
                voiced_full[s:e] * \
                f32(voiced_amp)

            byp = _make_bypass(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=0,
                voiced_rms=None)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                vf  = FRIC_VOICED_TRACT.get(
                    ph, VOICED_TRACT_FRACTION)
                amp = np.ones(n_s, dtype=DTYPE)
                fade_start = n_on + n_body
                if n_off > 0 and \
                   fade_start < n_s:
                    amp[fade_start:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(amp) * vf

            byp = _make_bypass(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=n_on,
                voiced_rms=prev_vrms)
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
                tract_source[s+vot_s:s+vot_e] = (
                    noise_full[
                        s+vot_s:s+vot_e] * ne2 +
                    voiced_full[
                        s+vot_s:s+vot_e] * ve2)
            tr_s = vot_e
            if tr_s < n_s:
                tract_source[s+tr_s:e] = \
                    voiced_full[s+tr_s:e]

        pos += n_s

    return f32(tract_source), bypass_segs


# ============================================================
# PHRASE NORMALIZATION
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
        all_v = np.concatenate(vowel_samples)
        ref   = np.percentile(
            all_v, NORM_PERCENTILE)
    else:
        ref = np.percentile(
            np.abs(signal), NORM_PERCENTILE)

    if ref > 1e-8:
        signal = signal / ref * NORM_TARGET

    return np.clip(signal, -1.0, 1.0)


# ============================================================
# PHRASE SYNTHESIS v10 rev4
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v10 rev4. All fixes active.
    Rev4 specific:
      DH BW widened → no F1 ring.
      S/Z/SH/ZH resonator BW widened
        → no high-freq ring.
      H LP order=1 → no pole ring.
    """
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

    tract_src, bypass_segs = \
        _build_source_and_bypass(specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos + len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

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
                a2 = -np.exp(
                    -2*np.pi*abw*T)
                a1 = (2*np.exp(-np.pi*abw*T) *
                      np.cos(2*np.pi*af*T))
                b0 = 1.0 - a1 - a2
                y  = (b0 * float(seg[i]) +
                      a1*y1 + a2*y2)
                y2 = y1; y1 = y
                anti[i] = y
            out[pos:pos+n_s] = \
                seg - f32(anti) * 0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012 * sr)
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
    dur = len(sig) / sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v10 rev4")
    print()
    print("  ARTIFACT: IIR resonator ringing")
    print("  in phoneme bodies.")
    print()
    print("  S/Z  Q=22→7.3  bw 400→1200Hz")
    print("  SH   Q=4.2→2.8 bw 600→900Hz")
    print("  ZH   Q=3.1→2.4 bw 700→900Hz")
    print("  DH   bw_mult × 3.0")
    print("  H    LP order 2→1, fc 2500→2000Hz")
    print()
    print("  All rev3 fixes preserved:")
    print("  DH/H attack 18ms")
    print("  S/Z relative to voiced RMS")
    print("  Normalize to vowel body")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Running onset diagnostic...")
    print()
    try:
        from onset_diagnostic import \
            run_onset_diagnostic
        results, n_pass, n_fail = \
            run_onset_diagnostic(
                synth_phrase, PITCH, sr=SR)
        print()
    except ImportError:
        print("  onset_diagnostic.py not found.")
        n_pass = 0
        n_fail = 0
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
    print("  Isolation tests...")
    isolation = [
        ('test_the',
         [('the',   ['DH', 'AH'])],
         'DH body: no low ring'),
        ('test_here',
         [('here',  ['H', 'IH', 'R'])],
         'H body: no mid ring'),
        ('test_was',
         [('was',   ['W', 'AH', 'Z'])],
         'Z body: no high ring'),
        ('test_voice',
         [('voice', ['V', 'OY', 'S'])],
         'S body: no high ring'),
        ('test_this_is_here',
         [('this',  ['DH', 'IH', 'S']),
          ('is',    ['IH', 'Z']),
          ('here',  ['H',  'IH', 'R'])],
         'DH + Z + H'),
        ('test_there_and_here',
         [('there', ['DH', 'EH', 'R']),
          ('and',   ['AE', 'N',  'D']),
          ('here',  ['H',  'IH', 'R'])],
         'DH then H'),
    ]
    for label, words, note in isolation:
        seg = synth_phrase(
            words, pitch_base=PITCH)
        write_wav(
            f"output_play/{label}.wav",
            apply_room(seg, rt60=1.2,
                        dr=0.55))
        print(f"    {label}.wav  ({note})")

    print()
    print("  Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            PHRASE, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            apply_room(seg, rt60=1.5,
                        dr=0.50))
        print(f"    the_voice_{label}.wav")

    print()
    print("  Coverage...")
    for label, words, punct in [
        ('water_home',
         [('water', ['W', 'AA', 'T', 'ER']),
          ('home',  ['H', 'OW', 'M'])], '.'),
        ('still_here',
         [('still', ['S', 'T', 'IH', 'L']),
          ('here',  ['H', 'IH', 'R'])], '.'),
        ('here_and_there',
         [('here',  ['H',  'IH', 'R']),
          ('and',   ['AE', 'N',  'D']),
          ('there', ['DH', 'EH', 'R'])], '.'),
        ('not_yet',
         [('not',   ['N', 'AA', 'T']),
          ('yet',   ['Y', 'EH', 'T'])], '.'),
        ('always_open',
         [('always', ['AA', 'L', 'W',
                       'EH', 'Z']),
          ('open',   ['OH', 'P', 'EH',
                       'N'])], '.'),
    ]:
        seg = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            apply_room(seg, rt60=1.6,
                        dr=0.48))
        print(f"    phrase_{label}.wav")

    print()
    print("=" * 60)
    print()
    if n_pass + n_fail > 0:
        print(f"  Onset: {n_pass}/{n_pass+n_fail}")
    print()
    print("  LISTEN FOR RING:")
    print("  afplay output_play/test_voice.wav")
    print("  → S body clean? no whistle?")
    print()
    print("  afplay output_play/test_was.wav")
    print("  → Z body clean? no whistle?")
    print()
    print("  afplay output_play/test_the.wav")
    print("  → DH body clean? no hum?")
    print()
    print("  afplay output_play/test_here.wav")
    print("  → H body clean? no tone?")
    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  If ring persists on S/Z:")
    print("  → increase S/Z bw further:")
    print("    S bw 1200 → 2000")
    print("    Z bw 1200 → 2000")
    print()
    print("  If ring persists on DH:")
    print("  → increase DH_BW_MULT:")
    print("    3.0 → 5.0")
    print()
    print("  If ring persists on H:")
    print("  → reduce H_BYPASS_LP_HZ:")
    print("    2000 → 1500")
    print()
