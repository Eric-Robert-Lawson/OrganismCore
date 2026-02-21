"""
VOICE PHYSICS v10
February 2026

SELF-CONTAINED.
Does not inherit synth_phrase or
build_source_and_bypass from any parent.
Import chain shadowing is broken.
Only leaf utilities are imported.

ONSET DIAGNOSTIC RESULTS (v2 diagnostic):

  DH: centroid=830Hz  target=(1800,6000) ✗
      rms_ratio=0.966 target=(<=0.60)    ✗
      periodicity=0.367                  ✓
      → tract silence working (rms<1.0)
      → bypass spectral shape wrong
        (broadband noise peaks below 1kHz)
      → FIX: DH bypass = BP(1800-6500Hz)

  H:  centroid=886Hz                     ✓
      periodicity=0.091                  ✓
      peak_prominence=33.63              ✗
      → periodicity fixed (aperiodic now)
      → prominence=33 may be measurement
        artifact (AA resonator leaking
        into window) OR real spike
      → FIX: H bypass uses explicit
        bandpass 200-7000Hz + no tract

  Z:  no_sibilance                       ✗
      → gain floor not reaching bypass
      → FIX: gain floor 0.65, explicit
        check before resonator call

THREE FIXES IN THIS FILE:

  FIX 1: DH
    Tract silent for DH_TRACT_BYPASS_MS.
    DH bypass = BP(1800-6500Hz) shaped noise.
    Voiced fades in after silence zone.
    Dental friction IS the onset.

  FIX 2: H
    Tract source = 0 for H entirely.
    H bypass = broadband aspiration,
    BP(200-7000Hz), no resonators.
    Tract uses NEUTRAL_F during H.
    IH begins from neutral — clean.

  FIX 3: Z / ZH
    Bypass gain floor = 0.65 for Z,
    0.40 for ZH.
    Applied before resonator call.
    Calibration cannot zero Z.

Import chain:
  v10 (self-contained)
    → imports leaf utilities from v9/v7
    → defines all synthesis functions here
"""

# ============================================================
# IMPORTS — LEAF UTILITIES ONLY
# No synth_phrase. No build_source_and_bypass.
# ============================================================

from voice_physics_v9 import (
    # Resonator engine
    tract,
    warm,
    resonator,
    # Output
    breath_rest,
    apply_room,
    write_wav,
    # Level tools
    TARGET_RMS, calibrate, rms,
    # Filter tools
    safe_bp, safe_lp, safe_hp,
    # Constants
    VOWEL_F, GAINS,
    WORD_SYLLABLES,
    get_f, get_b, scalar,
    PITCH, DIL, SR, DTYPE, f32,
    # Timing
    TRANS_MS, DEFAULT_TRANS_MS,
    trans_n,
    REST_MAX_MS,
    NEUTRAL_F, NEUTRAL_B,
    # Voiced fractions
    VOICED_TRACT_FRACTION,
    Z_VOICED_TRACT, ZH_VOICED_TRACT,
    V_VOICED_TRACT,
    FRIC_VOICED_TRACT,
    VOICED_FRICS,
    # Duration caps
    VOWEL_PHONEMES, DIPHTHONG_PHONEMES,
    VOWEL_MAX_MS, DIPHTHONG_MAX_MS,
    APPROX_MAX_MS, FRIC_MAX_MS,
    FINAL_FRIC_MAX_MS,
    DH_MAX_MS, H_MAX_MS,
    H_ASPIRATION_GAIN,
    # Bypass components
    RESONATOR_CFG, BROADBAND_CFG,
    cavity_resonator,
    get_calibrated_gains_v8,
    recalibrate_gains_v8,
    # Spec and prosody builders
    ph_spec_v9,
    plan_prosody,
    # Trajectory builder
    build_trajectories,
)

import numpy as np
from scipy.signal import lfilter, butter
import copy
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# v10 CONSTANTS
# ============================================================

# ── FIX 1: DH ─────��─────────────────────────────────────────
DH_TRACT_BYPASS_MS = 25    # tract silent at onset
DH_VOICED_FRACTION = 0.30  # target voiced in body
DH_BYPASS_BP_LO    = 1800  # Hz  dental range low
DH_BYPASS_BP_HI    = 6500  # Hz  dental range high
DH_BYPASS_GAIN     = 0.35  # DH is quiet friction

# ── FIX 2: H ────────────────────────────────────────────────
H_BYPASS_HP_HZ  = 200   # remove sub-bass
H_BYPASS_LP_HZ  = 7000  # remove ultrasonic
H_BYPASS_GAIN   = 0.55  # breathy level

# ── FIX 3: Z / ZH gain floors ───────────────────────────────
Z_BYPASS_GAIN_FLOOR  = 0.65
ZH_BYPASS_GAIN_FLOOR = 0.40


# ============================================================
# BYPASS GENERATORS
# All defined here. Called from here only.
# ============================================================

def _make_dh_bypass(n_s, sr=SR,
                     next_is_vowel=False,
                     onset_delay=0):
    """
    FIX 1: DH-specific bypass.
    Bandpass 1800-6500Hz.
    Shifts spectral centroid to ~3000-4000Hz.
    Dental friction character.
    onset_delay=0: friction starts at t=0.
    The friction IS the DH onset.
    """
    n_s         = int(n_s)
    onset_delay = max(0, int(onset_delay))
    if onset_delay >= n_s:
        return f32(np.zeros(n_s))

    n_eff = n_s - onset_delay
    noise = calibrate(
        f32(np.random.normal(0, 1, n_eff)))

    # Bandpass to dental range
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

    # Envelope
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(int(rel_ms / 1000.0 * sr),
                 n_eff // 4)
    atk    = min(int(0.005 * sr), n_eff // 4)
    env    = f32(np.ones(n_eff))
    if atk > 0 and atk < n_eff:
        env[:atk] = f32(np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(np.linspace(1, 0, rel))

    raw = np.zeros(n_s, dtype=DTYPE)
    raw[onset_delay:] = f32(shaped * env)
    return f32(raw)


def _make_h_bypass(n_s, sr=SR,
                    next_is_vowel=False):
    """
    FIX 2: H aspiration bypass.
    Pure broadband aspiration.
    HP(200Hz) + LP(7000Hz).
    No resonators. No tract.
    Goes directly to output.
    """
    n_s   = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))

    # HP: remove sub-bass
    try:
        b, a  = safe_hp(H_BYPASS_HP_HZ, sr)
        broad = f32(lfilter(b, a, noise))
    except:
        broad = noise.copy()

    # LP: remove ultrasonic
    try:
        nyq   = sr * 0.5
        wn    = min(H_BYPASS_LP_HZ / nyq, 0.98)
        b, a  = butter(2, wn, btype='low')
        broad = f32(lfilter(b, a, broad))
    except:
        pass

    broad = calibrate(broad) * H_BYPASS_GAIN

    # Envelope — H always starts with
    # some breath (0.2), never fully silent
    atk_ms = 8
    rel_ms = 20 if next_is_vowel else 12
    atk    = min(int(atk_ms / 1000.0 * sr),
                 n_s // 4)
    rel    = min(int(rel_ms / 1000.0 * sr),
                 n_s // 4)
    env    = f32(np.ones(n_s))
    if atk > 0:
        env[:atk] = f32(
            np.linspace(0.2, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1.0, 0.0, rel))

    return f32(broad * env)


def _make_bypass(ph, n_s, sr=SR,
                  next_is_vowel=False,
                  onset_delay=0):
    """
    General fricative bypass.
    FIX 3: Z/ZH have gain floors.
    Routes DH through _make_dh_bypass.
    All others through resonator/broadband
    as established in v6-v9.
    """
    # DH gets its own shaped bypass
    if ph == 'DH':
        return _make_dh_bypass(
            n_s, sr,
            next_is_vowel=next_is_vowel,
            onset_delay=onset_delay)

    gains = get_calibrated_gains_v8(sr=sr)
    gain  = gains.get(ph, None)

    # FIX 3: gain floors for Z and ZH
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

    if ph in RESONATOR_CFG:
        cfg   = RESONATOR_CFG[ph]
        g     = gain if gain is not None \
                else cfg['gain']
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        res   = cavity_resonator(
            noise, cfg['fc'], cfg['bw'], sr=sr)
        raw[onset_delay:] = _env(
            calibrate(res) * g)

    elif ph in BROADBAND_CFG:
        cfg   = BROADBAND_CFG[ph]
        g     = gain if gain is not None \
                else cfg['gain']
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        try:
            b, a  = safe_hp(cfg['hp_fc'], sr)
            broad = f32(lfilter(b, a, noise))
        except:
            broad = noise.copy()
        raw[onset_delay:] = _env(
            calibrate(broad) * g)

    return f32(raw)


# ============================================================
# TRAJECTORY BUILDER v10
# H phonemes use NEUTRAL_F as formant target.
# Tract rests at neutral during H.
# Following vowel starts from neutral — clean.
# ============================================================

def _build_trajectories(phoneme_specs, sr=SR):
    """
    v10: H phonemes use NEUTRAL_F/B.
    Prevents any tract resonance during H.
    All other phonemes unchanged.
    """
    patched = []
    for spec in phoneme_specs:
        if spec['ph'] == 'H':
            s = copy.copy(spec)
            s['F_tgt'] = list(NEUTRAL_F)
            s['B_tgt'] = list(NEUTRAL_B)
            if 'F_end' in s:
                s['F_end'] = list(NEUTRAL_F)
            patched.append(s)
        else:
            patched.append(spec)
    return build_trajectories(patched, sr=sr)


# ============================================================
# SOURCE BUILDER v10
# Self-contained. No parent version called.
# ============================================================

def _build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v10 source builder.

    FIX 1: DH
      Tract silent for DH_TRACT_BYPASS_MS.
      Bypass = BP(1800-6500Hz) at t=0.
      Voiced fades in after silence zone.

    FIX 2: H
      Tract source = 0.
      Bypass = flat broadband aspiration.

    FIX 3: Z/ZH
      Gain floor applied in _make_bypass.

    All other phonemes identical to v9.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # ── F0/oq trajectories ─────────���────────
    f0_traj = np.zeros(n_total, dtype=DTYPE)
    oq_traj = np.zeros(n_total, dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s     = spec['n_s']
        f0_this = spec.get('pitch', PITCH)
        oq_this = spec.get('oq', 0.65)
        f0_next = (
            phoneme_specs[si+1].get('pitch', PITCH)
            if si < len(phoneme_specs)-1
            else f0_this)
        oq_next = (
            phoneme_specs[si+1].get('oq', 0.65)
            if si < len(phoneme_specs)-1
            else oq_this)
        f0_traj[pos:pos+n_s] = np.linspace(
            f0_this, f0_next, n_s)
        oq_traj[pos:pos+n_s] = np.linspace(
            oq_this, oq_next, n_s)
        pos += n_s

    # ── Rosenberg pulse voiced source ────────
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

    n_dh_bypass = int(
        DH_TRACT_BYPASS_MS / 1000.0 * sr)

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

        n_on   = min(trans_n(ph, sr), n_s // 3)
        n_off  = min(trans_n(ph, sr), n_s // 3)
        n_body = max(0, n_s - n_on - n_off)

        # ── VOICED ──────────────────────────
        if stype == 'voiced':
            tract_source[s:e] = \
                voiced_full[s:e]

        # ── H — FIX 2 ───────────────────────
        elif stype == 'h':
            # Tract source stays zero.
            # H goes entirely through bypass.
            byp = _make_h_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        # ── DH — FIX 1 ──────────────────────
        elif stype == 'dh':
            # Tract silent for first n_dh_bypass.
            # Bypass (dental friction) starts t=0.
            # Voiced fades in after silence zone.
            n_silent = min(n_dh_bypass, n_s)
            n_remain = n_s - n_silent

            voiced_amp = np.zeros(n_s, dtype=DTYPE)
            if n_remain > 0:
                voiced_amp[n_silent:] = f32(
                    np.linspace(
                        0.0,
                        DH_VOICED_FRACTION,
                        n_remain))
                # Taper out over offset zone
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

            # Bypass t=0 (friction is onset)
            byp = _make_bypass(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=0)
            bypass_segs.append((s, byp))

        # ── FRICATIVES ──────────────────────
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

            # Full n_on delay — no vowel overlap
            byp = _make_bypass(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=n_on)
            bypass_segs.append((s, byp))

        # ── STOPS ───────────────────────────
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
                ne2 = f32(np.linspace(1,0,vot_n))
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
# PHRASE SYNTHESIS v10
# Self-contained.
# Calls _build_trajectories and
# _build_source_and_bypass defined above.
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v10 synth_phrase. Self-contained.
    All three onset fixes active.
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

    # v10 trajectory builder
    F_full, B_full, _ = \
        _build_trajectories(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # v10 source builder
    tract_src, bypass_segs = \
        _build_source_and_bypass(specs, sr=sr)

    # Tract (vowels and voiced consonants)
    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    # Add bypass signals post-tract
    for pos, byp in bypass_segs:
        e = min(pos + len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

    # Nasal antiformants
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

    # Amplitude envelope
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

    # Rests between words
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
    p95   = np.percentile(np.abs(final), 95)
    if p95 > 1e-8:
        final = final / p95 * 0.88
    final = np.clip(final, -1.0, 1.0)
    return final


# ============================================================
# CONVENIENCE FUNCTIONS
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
    print("VOICE PHYSICS v10")
    print("Self-contained. Three onset fixes.")
    print()
    print("  FIX 1: DH")
    print("    Tract silent first 25ms.")
    print("    Bypass = BP(1800-6500Hz).")
    print("    Voiced fades in after.")
    print("    Centroid target: 1800-6000Hz.")
    print()
    print("  FIX 2: H")
    print("    Tract source = 0.")
    print("    Bypass = HP(200)+LP(7000).")
    print("    No resonators.")
    print("    Tract holds NEUTRAL during H.")
    print()
    print("  FIX 3: Z/ZH")
    print("    Z gain floor = 0.65.")
    print("    ZH gain floor = 0.40.")
    print("    Calibration cannot zero Z.")
    print()
    print("  STRUCTURAL")
    print("    No parent synth_phrase.")
    print("    No parent build_source_and_bypass.")
    print("    _functions are private.")
    print("    No import shadowing.")
    print("=" * 60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    # Run onset diagnostic first
    print("  Running onset diagnostic v2...")
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
        print("  Run it separately.")
        n_pass = 0
        n_fail = 0
        print()

    # Primary phrase
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

    # Isolation tests — one per artifact
    print()
    print("  Isolation tests...")
    isolation = [
        ('test_the',
         [('the',   ['DH', 'AH'])],
         'no ea-prefix'),
        ('test_here',
         [('here',  ['H', 'IH', 'R'])],
         'breathy, no CH-prefix'),
        ('test_was',
         [('was',   ['W', 'AH', 'Z'])],
         'Z buzz present'),
        ('test_voice',
         [('voice', ['V', 'OY', 'S'])],
         'S clean after OY'),
        ('test_this_is_here',
         [('this',  ['DH', 'IH', 'S']),
          ('is',    ['IH', 'Z']),
          ('here',  ['H',  'IH', 'R'])],
         'DH + Z + H in phrase'),
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
            apply_room(seg,
                        rt60=1.2, dr=0.55))
        print(f"    {label}.wav  ({note})")

    # Sentence types
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            PHRASE,
            punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            apply_room(
                seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Coverage
    print()
    print("  Coverage phrases...")
    coverage = [
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
    ]
    for label, words, punct in coverage:
        seg = synth_phrase(
            words,
            punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            apply_room(
                seg, rt60=1.6, dr=0.48))
        print(f"    phrase_{label}.wav")

    # Summary
    print()
    print("=" * 60)
    print()
    if n_pass + n_fail > 0:
        print(f"  Onset diagnostic: "
              f"{n_pass}/{n_pass+n_fail}")
        if n_fail == 0:
            print("  All onset checks passing.")
        else:
            print("  See diagnostic output above.")
    print()
    print("  START:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  ISOLATION:")
    print("  afplay output_play/test_the.wav")
    print("  afplay output_play/test_here.wav")
    print("  afplay output_play/test_was.wav")
    print("  afplay output_play/test_voice.wav")
    print()
    print("  DH + H TOGETHER:")
    print("  afplay output_play/"
          "test_there_and_here.wav")
    print()
    print("  If onset diagnostic passes")
    print("  and artifacts remain:")
    print("  → the perceptual problem is")
    print("    in a different mechanism")
    print("    than onset timing.")
    print("  → report exactly what you hear")
    print("    and when in the phrase.")
    print()
