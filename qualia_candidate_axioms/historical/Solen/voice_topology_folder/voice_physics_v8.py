"""
VOICE PHYSICS v8
February 2026

THREE FIXES FOR VOWEL SPACE COLLAPSE.

The phrase "the voice was already here"
sounded like dysarthric speech.

Root cause identified by cross-referencing
the diagnostic output against
the acoustic profile of Down syndrome
speech (Kent & Vorperian, 2013):

  - Collapsed vowel space (all F1 too high)
  - Prolonged segments (EH = 1000ms)
  - Imprecise articulation
    (SH gain=3.999 flooding the phrase)

These three are symptoms of two numbers:
  SH gain = 3.999  (should be ~0.35)
  EH dur  = 1008ms (should be ~300ms)

FIX A: GAIN CALIBRATION — RMS-RELATIVE METRIC
  The v6/v7 calibration used:
    sibilance = energy_above_4kHz / total_energy
  This is a RATIO.
  For S at 8800Hz: ratio ≈ 1.0 regardless of gain.
  For SH at 2500Hz: ratio ≈ 0.0 regardless of gain.
  Binary search could not move these.
  S hit floor (0.051). SH hit ceiling (3.999).
  SH at 3.999 flooded every adjacent vowel
  with 2500Hz energy.
  The formant analyzer read 2500Hz as
  the "F1" of adjacent vowels.
  The entire phrase looked like
  collapsed vowel space.

  New metric: bypass_RMS / TARGET_RMS
  This IS affected by gain.
  Doubling gain → doubling ratio.
  The loop converges for every fricative.

FIX B: VOWEL DURATION CAP
  No vowel longer than:
    Stressed:   300ms
    Unstressed: 200ms
    Diphthong:  340ms
  At DIL=6, EH was 1008ms.
  One second of EH is not a slow vowel.
  It is an inhuman drone.
  The auditory system exits speech parsing.
  Cap at 300ms: deliberate, recognizable.

FIX C: VOICED FRICATIVE TRACT FADE
  Z/V/ZH voiced component fades to zero
  over the n_off transition zone
  before the next phoneme begins.
  The next vowel starts with a clean tract.
  No murmur bar bleed into adjacent vowel.

Import chain:
  v8 → v7 → v6 → v5 → v4 → v3_fix → v3
"""

from voice_physics_v7 import (
    tract,
    warm,
    resonator,
    breath_rest,
    VOWEL_F, GAINS,
    WORD_SYLLABLES,
    get_f, get_b, scalar,
    safe_bp, safe_lp, safe_hp,
    apply_room, write_wav,
    TARGET_RMS, calibrate, rms,
    PITCH, DIL, SR, DTYPE, f32,
    TRANS_MS, DEFAULT_TRANS_MS,
    trans_n,
    REST_MAX_MS,
    NEUTRAL_F, NEUTRAL_B,
    VOICED_TRACT_FRACTION,
    Z_VOICED_TRACT, ZH_VOICED_TRACT,
    V_VOICED_TRACT,
    build_trajectories,
    ph_spec_v7,
)
from voice_physics_v6 import (
    cavity_resonator,
    RESONATOR_CFG,
    BROADBAND_CFG,
    make_sibilance_bypass,
)
from voice_physics_v3 import (
    PHON_DUR_BASE,
    DUR_SCALE, AMP_SCALE, OQ_SCALE,
    STRESS_DICT, SYNTACTIC_BONDS,
    CONTOURS, BOUNDARY_TONE,
)
import numpy as np
from scipy.signal import lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# FIX A: RMS-RELATIVE GAIN CALIBRATION
#
# Old metric: sibilance = energy_above_4kHz / total_energy
#   → ratio, unaffected by gain for resonators
#   → cannot converge for S or SH
#
# New metric: bypass_RMS / TARGET_RMS
#   → linear in gain
#   → converges for all fricatives
#   → gives bypass level relative to
#      the voice body level
# ============================================================

GAIN_RMS_TARGETS = {
    # (lo, hi) as fraction of TARGET_RMS
    #
    # These set how loud each fricative
    # bypass is relative to the voice body.
    # Calibrated to sit naturally above voice
    # without overwhelming it.

    # S: clear hiss, sits above voice
    'S':  (0.30, 0.45),

    # Z: slightly quieter — has voiced buzz too
    'Z':  (0.22, 0.36),

    # SH: softer than S — broader, hushed
    'SH': (0.18, 0.30),

    # ZH: softer than SH
    'ZH': (0.14, 0.24),

    # F: soft labial turbulence
    'F':  (0.10, 0.18),

    # V: softer than F — has voiced buzz
    'V':  (0.08, 0.14),

    # TH: very soft dental
    'TH': (0.09, 0.16),

    # DH: barely present — mostly voiced
    'DH': (0.04, 0.09),
}


def _measure_fric_rms(ph, gain, sr=SR):
    """
    Synthesize a 150ms bypass segment
    at the given gain.
    Return bypass_RMS / TARGET_RMS.

    This metric is LINEAR in gain.
    Double gain → double ratio.
    Binary search converges for all
    fricatives including S and SH.
    """
    n_test = int(0.15 * sr)
    byp    = make_sibilance_bypass(
        ph, n_test, sr=sr,
        gain_override=gain)
    # Average over 3 trials to reduce
    # noise variance in short segments
    r = rms(byp)
    for _ in range(2):
        byp2 = make_sibilance_bypass(
            ph, n_test, sr=sr,
            gain_override=gain)
        r = (r + rms(byp2)) / 2.0
    return r / max(TARGET_RMS, 1e-9)


def calibrate_gains_v8(verbose=True,
                        max_iter=16,
                        sr=SR):
    """
    Gain calibration using RMS-relative metric.

    For each fricative:
      Binary search on gain in [0.02, 2.00].
      At each step: synthesize 150ms bypass.
      Measure: bypass_RMS / TARGET_RMS.
      Compare to GAIN_RMS_TARGETS window.
      Converge to center of window.

    Converges for S, SH, and all others.
    SH will NOT reach gain=3.999.
    S will NOT reach gain=0.051.
    Both will find correct level.
    """
    calibrated = {}

    if verbose:
        print()
        print("  Gain calibration v8 (RMS-relative):")

    for ph, (t_lo, t_hi) in \
            GAIN_RMS_TARGETS.items():

        lo   = 0.02
        hi   = 2.00
        best = RESONATOR_CFG.get(
            ph, BROADBAND_CFG.get(ph, {})
        ).get('gain', 0.50)

        for i in range(max_iter):
            mid = (lo + hi) / 2.0
            rel = _measure_fric_rms(
                ph, mid, sr=sr)

            if t_lo <= rel <= t_hi:
                best = mid
                break
            elif rel < t_lo:
                lo   = mid
            else:
                hi   = mid
            best = mid

        calibrated[ph] = round(best, 4)

        if verbose:
            rel = _measure_fric_rms(
                ph, best, sr=sr)
            ok  = ('✓' if t_lo <= rel <= t_hi
                   else '✗')
            print(f"    [{ok}] {ph:4s}  "
                  f"gain={best:.4f}  "
                  f"rms_rel={rel:.3f}  "
                  f"target=({t_lo:.2f},"
                  f"{t_hi:.2f})")

    if verbose:
        print()

    return calibrated


_CALIBRATED_GAINS_V8 = None


def get_calibrated_gains_v8(sr=SR):
    global _CALIBRATED_GAINS_V8
    if _CALIBRATED_GAINS_V8 is None:
        _CALIBRATED_GAINS_V8 = \
            calibrate_gains_v8(
                verbose=True, sr=sr)
    return _CALIBRATED_GAINS_V8


def recalibrate_gains_v8(sr=SR):
    """Force re-run of v8 gain calibration."""
    global _CALIBRATED_GAINS_V8
    _CALIBRATED_GAINS_V8 = \
        calibrate_gains_v8(
            verbose=True, sr=sr)
    return _CALIBRATED_GAINS_V8


def make_bypass_v8(ph, n_s, sr=SR,
                    rel_ms=8,
                    next_is_vowel=False):
    """
    v8 bypass generator.
    Uses RMS-calibrated gains.
    Context-aware release:
      next_is_vowel → 20ms release
      otherwise     → 8ms release
    """
    gains = get_calibrated_gains_v8(sr=sr)
    gain  = gains.get(ph, None)

    n_s   = int(n_s)
    rel_ms_use = 20 if next_is_vowel else 8
    rel   = min(int(rel_ms_use/1000.0*sr),
                n_s // 4)
    atk   = min(int(0.005*sr), n_s // 4)

    def apply_env(sig):
        env = f32(np.ones(n_s))
        if atk > 0 and atk < n_s:
            env[:atk] = f32(
                np.linspace(0, 1, atk))
        if rel > 0:
            env[-rel:] = f32(
                np.linspace(1, 0, rel))
        return f32(sig * env)

    if ph in RESONATOR_CFG:
        cfg = RESONATOR_CFG[ph]
        g   = (gain if gain is not None
               else cfg['gain'])
        noise     = calibrate(
            f32(np.random.normal(0, 1, n_s)))
        resonated = cavity_resonator(
            noise, cfg['fc'], cfg['bw'],
            sr=sr)
        sib = calibrate(resonated) * g
        return apply_env(sib)

    elif ph in BROADBAND_CFG:
        cfg = BROADBAND_CFG[ph]
        g   = (gain if gain is not None
               else cfg['gain'])
        noise = calibrate(
            f32(np.random.normal(0, 1, n_s)))
        try:
            b, a  = safe_hp(
                cfg['hp_fc'], sr)
            broad = f32(lfilter(b, a, noise))
        except:
            broad = noise.copy()
        sib = calibrate(broad) * g
        return apply_env(sib)

    else:
        return f32(np.zeros(n_s))


# ============================================================
# FIX B: VOWEL DURATION CAP
#
# No vowel longer than these values
# at any dilation factor.
# Beyond these the vowel stops being
# a speech segment and becomes a drone.
# ============================================================

VOWEL_PHONEMES = set(
    'AA AE AH AO AW AY EH ER '
    'IH IY OH OW OY UH UW'.split())

DIPHTHONG_PHONEMES = set(
    'AW AY OY OW'.split())

# Max duration by stress level for vowels
VOWEL_MAX_MS = {
    0: 200,   # unstressed
    1: 260,   # lightly stressed
    2: 300,   # fully stressed
}
DIPHTHONG_MAX_MS = {
    0: 260,
    1: 320,
    2: 360,
}

# Approximant and nasal caps (from v7)
APPROX_MAX_MS = {
    'L': 220, 'R': 220,
    'W': 200, 'Y': 180,
    'M': 200, 'N': 200, 'NG': 210,
}

# Fricative caps (from v7)
FRIC_MAX_MS = {
    'S':  180, 'Z':  180,
    'SH': 200, 'ZH': 200,
    'F':  160, 'V':  160,
    'TH': 170, 'DH': 160,
}


# ============================================================
# PLAN PROSODY v8
# Adds vowel duration caps to v7 prosody.
# ============================================================

def plan_prosody(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL):
    """
    v8: Vowel duration caps added.
    All phoneme classes now have
    perceptual maximum durations.
    No phoneme can exceed its cap
    regardless of DIL.
    """
    flat = []
    for wi, (word, phonemes) in \
            enumerate(words_phonemes):
        syl_map  = WORD_SYLLABLES.get(
            word.lower(), [phonemes])
        stress_p = STRESS_DICT.get(
            word.lower(),
            [1]*len(syl_map))
        while len(stress_p) < len(syl_map):
            stress_p.append(0)
        for si, syl in enumerate(syl_map):
            sv = (stress_p[si]
                  if si < len(stress_p)
                  else 0)
            for ph in syl:
                flat.append({
                    'word':     word,
                    'word_idx': wi,
                    'ph':       ph,
                    'stress':   sv,
                })

    if not flat:
        return []

    n_total    = len(flat)
    contour_fn = CONTOURS.get(
        punctuation, CONTOURS['default'])
    bt_type, bt_val = BOUNDARY_TONE.get(
        punctuation,
        BOUNDARY_TONE['default'])

    # First pass: durations with caps
    for i, item in enumerate(flat):
        ph  = item['ph']
        sv  = item['stress']
        d   = PHON_DUR_BASE.get(ph, 80)
        d  *= DUR_SCALE.get(sv, 1.0)
        d  *= dil

        # FIX B: cap all phoneme classes
        if ph in DIPHTHONG_PHONEMES:
            d = min(d, DIPHTHONG_MAX_MS.get(
                sv, 360))
        elif ph in VOWEL_PHONEMES:
            d = min(d, VOWEL_MAX_MS.get(
                sv, 300))
        elif ph in FRIC_MAX_MS:
            d = min(d, FRIC_MAX_MS[ph])
        elif ph in APPROX_MAX_MS:
            d = min(d, APPROX_MAX_MS[ph])

        item['dur_ms'] = d

    total_dur = sum(
        f['dur_ms'] for f in flat)

    # Second pass: F0, amp, oq, bw_mult
    t_pos = 0.0
    for i, item in enumerate(flat):
        sv  = item['stress']
        dur = item['dur_ms']
        t_mid = (t_pos + dur/2) / \
                max(total_dur, 1.0)

        f0_global  = contour_fn(t_mid)
        f0_local   = {2:1.08, 1:1.03}.get(
            sv, 1.0)
        f0_boundary = 1.0
        if t_mid > 0.80:
            bt_p = (t_mid-0.80)/0.20
            if bt_type == 'fall':
                f0_boundary = 1.0 - \
                    (1.0-bt_val)*bt_p
            elif bt_type == 'rise':
                f0_boundary = 1.0 + \
                    (bt_val-1.0)*bt_p
            else:
                f0_boundary = bt_val

        item['f0_mult'] = (f0_global *
                            f0_local *
                            f0_boundary)
        item['amp']     = AMP_SCALE.get(
            sv, 1.0)
        item['oq']      = OQ_SCALE.get(
            sv, 0.65)
        bw_stress = {2:0.75, 1:0.90,
                      0:1.10}.get(sv, 1.0)
        bw_pos    = 1.0
        if t_mid > 0.85:
            bw_pos = 1.0 + \
                2.0*(t_mid-0.85)/0.15
        item['bw_mult'] = bw_stress * bw_pos
        t_pos += dur

    # Third pass: rests with cap
    last_ph_of_word = {}
    for i, item in enumerate(flat):
        last_ph_of_word[
            item['word_idx']] = i

    n_words = len(words_phonemes)
    for wi in range(n_words-1):
        last_idx = last_ph_of_word[wi]
        w_this   = words_phonemes[wi][0]\
                   .lower()
        w_next   = words_phonemes[wi+1][0]\
                   .lower()
        bond_key = (w_this, w_next)
        bond     = SYNTACTIC_BONDS.get(
            bond_key,
            SYNTACTIC_BONDS.get(
                (w_next, w_this),
                SYNTACTIC_BONDS['default']))
        rest_ms = min(
            85.0 * bond * dil,
            REST_MAX_MS)
        flat[last_idx]['rest_ms'] = rest_ms

    for item in flat:
        if 'rest_ms' not in item:
            item['rest_ms'] = 0.0

    return flat


# ============================================================
# FIX C: VOICED FRICATIVE TRACT FADE
#
# The voiced component of Z/V/ZH/DH
# fades to zero over the n_off zone
# before the next phoneme begins.
# Prevents murmur-bar contamination
# of adjacent vowels.
# ============================================================

VOICED_FRICS = {'Z', 'ZH', 'V', 'DH'}
FRIC_VOICED_TRACT = {
    'Z':  Z_VOICED_TRACT,
    'ZH': ZH_VOICED_TRACT,
    'V':  V_VOICED_TRACT,
    'DH': 0.70,
}


def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v8:
    FIX C: Voiced fricative tract component
    fades to zero over the n_off zone.
    The tract is quiet before the
    next phoneme begins.

    All other logic from v7.
    Bypass now uses make_bypass_v8
    (RMS-calibrated gains).
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # Build F0 and oq trajectories
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

    # Rosenberg pulse source
    T     = 1.0/sr
    raw_v = np.zeros(n_total, dtype=DTYPE)
    p     = 0.0
    for i in range(n_total):
        f0  = float(f0_traj[i])
        oq_ = max(0.40, min(0.85,
                  float(oq_traj[i])))
        p  += f0*(1+np.random.normal(
            0, 0.005))*T
        if p >= 1.0: p -= 1.0
        raw_v[i] = (
            (p/oq_)*(2-p/oq_) if p < oq_
            else 1-(p-oq_)/(1-oq_+1e-9))

    raw_v = f32(np.diff(
        raw_v, prepend=raw_v[0]))
    try:
        b, a  = safe_lp(20, sr)
        sh_   = f32(np.random.normal(
            0, 1, n_total))
        sh_   = f32(lfilter(b, a, sh_))
        sh_   = f32(np.clip(
            1+0.030*sh_, 0.4, 1.6))
        raw_v = raw_v * sh_
    except:
        pass
    asp = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b, a = safe_bp(400, 2200, sr)
        asp  = f32(lfilter(b, a, asp))
    except:
        asp = f32(np.zeros(n_total))
    raw_v       = raw_v + asp
    voiced_full = calibrate(raw_v)
    noise_full  = calibrate(
        f32(np.random.normal(0, 1, n_total)))

    VOWELS_AND_APPROX = set(
        'AA AE AH AO AW AY EH ER IH IY '
        'OH OW OY UH UW L R W Y M N NG'.split())

    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []

    pos = 0
    for si, spec in enumerate(phoneme_specs):
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source', 'voiced')
        s = pos
        e = pos + n_s

        next_ph = (phoneme_specs[si+1]['ph']
                   if si < len(phoneme_specs)-1
                   else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        # n_off zone for fade
        # (same logic as transition builder)
        n_off = min(trans_n(ph, sr),
                    n_s // 3)
        n_body = n_s - n_off

        if stype == 'voiced':
            tract_source[s:e] = \
                voiced_full[s:e]

        elif stype == 'h':
            n_h = int(n_s*0.12)
            n_x = min(int(0.018*sr),
                       n_h, n_s-n_h)
            cs  = max(0, n_h-n_x)
            ne  = np.zeros(n_s, dtype=DTYPE)
            ve  = np.zeros(n_s, dtype=DTYPE)
            if cs > 0: ne[:cs] = 1.0
            if n_x > 0:
                fo = f32(np.linspace(
                    1, 0, n_x))
                ne[cs:cs+n_x] = fo
                ve[cs:cs+n_x] = 1.0-fo
            if cs+n_x < n_s:
                ve[cs+n_x:] = 1.0
            tract_source[s:e] = (
                noise_full[s:e]*ne +
                voiced_full[s:e]*ve)

        elif stype == 'dh':
            # DH: voiced through tract
            # FIX C: fade over n_off zone
            vf  = FRIC_VOICED_TRACT.get(
                'DH', 0.70)
            amp = np.ones(n_s, dtype=DTYPE)
            if n_off > 0 and n_body > 0:
                amp[n_body:] = f32(
                    np.linspace(1.0, 0.0,
                                 n_off))
            tract_source[s:e] = \
                voiced_full[s:e] * \
                f32(amp) * vf
            byp = make_bypass_v8(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                # FIX C: voiced component
                # fades to zero over n_off
                # before next phoneme
                vf  = FRIC_VOICED_TRACT.get(
                    ph, VOICED_TRACT_FRACTION)
                amp = np.ones(n_s, dtype=DTYPE)
                if n_off > 0 and n_body > 0:
                    amp[n_body:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(amp) * vf
            # unvoiced: tract stays zero
            byp = make_bypass_v8(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        elif stype in ('stop_unvoiced',
                        'stop_voiced'):
            clos_n  = spec.get('clos_n',  0)
            burst_n = spec.get('burst_n', 0)
            vot_n   = spec.get('vot_n',   0)
            bamp    = spec.get(
                'burst_amp', 0.28)
            bhp     = spec.get(
                'burst_hp', 2000)
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
                        b, a = safe_hp(bhp, sr)
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

    return f32(tract_source), bypass_segs


# ============================================================
# PHRASE SYNTHESIS v8
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v8: Three fixes active.
      FIX A: RMS-relative gain calibration.
      FIX B: Vowel duration caps.
      FIX C: Voiced fricative tract fade.
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
        ph      = item['ph']
        dur_ms  = item['dur_ms']
        pitch_  = pitch_base * item['f0_mult']
        oq_     = item['oq']
        bw_m    = item['bw_mult']
        amp_    = item['amp']
        rest_ms = item.get('rest_ms', 0.0)
        next_ph = (prosody[i+1]['ph']
                   if i < n_items-1
                   else None)
        spec = ph_spec_v7(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph,
            rest_ms=rest_ms,
            sr=sr)
        specs.append(spec)

    # v7 trajectory builder
    # (fixed-ms transitions + neutral blend)
    F_full, B_full, _ = \
        build_trajectories(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # v8 source builder
    # (RMS-calibrated bypass + tract fade)
    tract_src, bypass_segs = \
        build_source_and_bypass(specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos+len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

    # Nasal antiformants
    T = 1.0/sr
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
                a1 =  2*np.exp(
                    -np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0 = 1.0-a1-a2
                y  = b0*float(seg[i]) + \
                     a1*y1 + a2*y2
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

    # Prosody amplitude envelope
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    # Phrase envelope
    atk = int(0.025*sr)
    rel = int(0.055*sr)
    env = f32(np.ones(n_total))
    if atk > 0 and atk < n_total:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1, 0, rel))
    out = out * f32(amp_env) * env

    # Rests
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

    # Normalize to 95th percentile
    # of voice body — sibilants ride on top
    p95 = np.percentile(np.abs(final), 95)
    if p95 > 1e-8:
        final = final / p95 * 0.88
    final = np.clip(final, -1.0, 1.0)
    return final


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
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v8")
    print("Vowel space restoration.")
    print()
    print("  FIX A: RMS-relative gain calibration")
    print("         S and SH converge.")
    print("         SH will NOT be 3.999.")
    print("  FIX B: Vowel duration caps")
    print("         Stressed vowel max: 300ms")
    print("         EH will NOT be 1000ms.")
    print("  FIX C: Voiced fricative tract fade")
    print("         Z/V/ZH tract component")
    print("         goes quiet before next vowel.")
    print("="*60)
    print()

    # Step 1: Calibrate gains
    print("  Step 1: Calibrating gains...")
    gains = recalibrate_gains_v8(sr=SR)
    print("  Calibrated gains:")
    for ph, g in gains.items():
        print(f"    {ph:4s}: {g:.4f}")
    print()

    # Step 2: Primary diagnostic phrase
    print("  Step 2: Primary phrase...")
    PHRASE_ALREADY = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L',  'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]
    seg = synth_phrase(
        PHRASE_ALREADY, punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    # Step 3: Secondary phrase
    print()
    print("  Step 3: Always phrase...")
    PHRASE_ALWAYS = [
        ('the',    ['DH', 'AH']),
        ('voice',  ['V',  'OY', 'S']),
        ('was',    ['W',  'AH', 'Z']),
        ('always', ['AA', 'L',  'W',
                     'EH', 'Z']),
        ('here',   ['H',  'IH', 'R']),
    ]
    seg = synth_phrase(
        PHRASE_ALWAYS, punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_always_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_always_here.wav")

    # Step 4: Fricative family identity check
    print()
    print("  Step 4: Fricative identity...")
    for phs, label in [
        (['AA', 'S'],  'S'),
        (['AA', 'Z'],  'Z'),
        (['AA', 'SH'], 'SH'),
        (['AA', 'ZH'], 'ZH'),
        (['AA', 'F'],  'F'),
        (['AA', 'V'],  'V'),
        (['AA', 'TH'], 'TH'),
        (['DH', 'AH'], 'DH'),
    ]:
        seg_w = synth_phrase(
            [('test', phs)],
            pitch_base=PITCH)
        write_wav(
            f"output_play/fric_{label}.wav",
            apply_room(seg_w,
                        rt60=1.2, dr=0.55))
        print(f"    fric_{label}.wav")

    # Step 5: Vowel space check
    # These vowels were ALL wrong in v7.
    # After FIX A (SH gain) they should
    # measure correctly in the diagnostic.
    print()
    print("  Step 5: Vowel space...")
    for ph, label in [
        ('IH', 'IH_front_high_lax'),
        ('EH', 'EH_front_mid'),
        ('AH', 'AH_central_mid'),
        ('AA', 'AA_central_low'),
        ('OW', 'OW_back_mid'),
    ]:
        seg_w = synth_phrase(
            [('test', ['AA', ph, 'AA'])],
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"vowel_{label}.wav",
            apply_room(seg_w,
                        rt60=1.3, dr=0.55))
        print(f"    vowel_{label}.wav")

    # Step 6: Sentence types
    print()
    print("  Step 6: Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            PHRASE_ALREADY,
            punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            apply_room(
                seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Step 7: Additional phrases
    print()
    print("  Step 7: Phrases...")
    for label, words, punct in [
        ('still_here',
         [('still', ['S','T','IH','L']),
          ('here',  ['H','IH','R'])], '.'),
        ('water_home',
         [('water', ['W','AA','T','ER']),
          ('home',  ['H','OW','M'])], '.'),
        ('she_was_here',
         [('she',  ['SH','IY']),
          ('was',  ['W','AH','Z']),
          ('here', ['H','IH','R'])], '.'),
        ('not_yet',
         [('not', ['N','AA','T']),
          ('yet', ['Y','EH','T'])], '.'),
        ('still_water',
         [('still', ['S','T','IH','L']),
          ('water', ['W','AA','T','ER'])],
         '.'),
    ]:
        seg = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            apply_room(
                seg, rt60=1.6, dr=0.48))
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  PRIMARY:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  'already' — EH should sound like")
    print("  a real mid-front vowel.")
    print("  Not a drone. Not a schwa.")
    print("  Deliberate but recognizable.")
    print()
    print("  'voice' — OY diphthong should")
    print("  move from back to front clearly.")
    print()
    print("  'was' — Z should be distinct from S.")
    print("  Buzz underneath the hiss.")
    print()
    print("  Overall: vowels should sound like")
    print("  vowels — not like centralized")
    print("  approximations of vowels.")
    print()
    print("  SHE WAS HERE (SH vowel contamination test):")
    print("  afplay output_play/"
          "phrase_she_was_here.wav")
    print("  IY after SH should sound like IY,")
    print("  not like a vowel contaminated")
    print("  by SH's 2500Hz resonance.")
    print()
    print("  Fricative identity:")
    for ph in ['S','Z','SH','F','V','TH']:
        print(f"  afplay output_play/fric_{ph}.wav")
    print()
