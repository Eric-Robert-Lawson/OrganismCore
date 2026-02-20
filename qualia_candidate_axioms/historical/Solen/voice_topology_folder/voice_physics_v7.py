"""
VOICE PHYSICS v7
February 2026

FOUR FIXES FROM PERCEPTUAL REPORT:

The phrase "the voice was always here"
was heard as:
"Voisss wazs already (teh) here"

Root causes and fixes:

FIX 1: FIXED-MS TRANSITIONS
  Transition zones were cf × n_s.
  At DIL=6 this gave ~80ms transitions.
  The ear heard them as extra phonemes.
  Fix: transition zones are fixed in ms,
  not proportional to phoneme duration.
  Bodies stretch with dilation.
  Boundaries do not.

FIX 2: FRICATIVE DURATION CAP
  S at DIL=6 was 840ms.
  That is not a slow S.
  It is a broken S.
  Fix: cap fricative durations at
  a perceptual maximum regardless of DIL.
  S max: 180ms. Z max: 180ms. etc.

FIX 3: Z VOICED CONTRAST
  Z sounded like more S.
  Voiced component buried.
  Fix: Z-specific voiced tract fraction
  raised to 0.88 (vs global 0.75).
  Z's voice is clearly present.
  The S/Z contrast is audible.

FIX 4: REST CAP + TRACT NEUTRAL BLEND
  Rests scaled with DIL → 300ms+.
  Tract didn't reset between words.
  IY → long rest → H-IH
  sounded like "teh here."
  Fix: cap rests at 240ms.
  Blend tract toward neutral
  during rests > 80ms.
  H picks up from near-neutral,
  not from previous extreme.

Import chain:
  v7 → v6 → v5 → v4 → v3_fix → v3
"""

from voice_physics_v6 import (
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
    make_sibilance_bypass_calibrated,
    VOICED_TRACT_FRACTION,
    recalibrate_gains,
)
from voice_physics_v3 import (
    plan_prosody as _plan_prosody_v3,
    PHON_DUR_BASE,
    DUR_SCALE, AMP_SCALE, OQ_SCALE,
    STRESS_DICT, SYNTACTIC_BONDS,
    CONTOURS, BOUNDARY_TONE,
    ph_spec_prosody as _ph_spec_v3,
)
import numpy as np
from scipy.signal import lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# FIX 1: FIXED-MS TRANSITION TABLE
#
# Transition time in absolute milliseconds.
# Does NOT scale with dilation.
# Only the phoneme BODY scales.
# ============================================================

TRANS_MS = {
    # Approximants: tongue/lip movement
    # ~25-35ms regardless of speech rate
    'L':  28, 'R':  28,
    'W':  28, 'Y':  28,

    # Nasals: velum movement
    # ~20-28ms
    'M':  24, 'N':  24, 'NG': 24,

    # Fricatives: constriction formation
    # ~12-18ms
    'S':  14, 'Z':  16,
    'SH': 16, 'ZH': 16,
    'F':  14, 'V':  16,
    'TH': 16, 'DH': 22,

    # Stops: closure formation
    # ~8-14ms
    'P':  10, 'B':  10,
    'T':  10, 'D':  10,
    'K':  12, 'G':  12,

    # H: breathy onset — slightly longer
    'H':  14,
}
DEFAULT_TRANS_MS = 22  # vowels


def trans_n(ph, sr=SR):
    """
    Transition duration in samples.
    Fixed in absolute time.
    Independent of dilation.
    """
    ms = TRANS_MS.get(ph, DEFAULT_TRANS_MS)
    return int(ms / 1000.0 * sr)


# ============================================================
# FIX 2: FRICATIVE DURATION CAP
#
# Maximum perceptual duration for fricatives.
# Above these values the sound is
# perceived as noise, not speech.
# ============================================================

FRIC_MAX_MS = {
    'S':  180, 'Z':  180,
    'SH': 200, 'ZH': 200,
    'F':  160, 'V':  160,
    'TH': 170, 'DH': 160,
}

# Also cap approximants and nasals
# (though less critical)
APPROX_MAX_MS = {
    'L': 220, 'R': 220,
    'W': 200, 'Y': 180,
    'M': 200, 'N': 200, 'NG': 210,
}

# Rest maximum — never longer than this
REST_MAX_MS = 240.0

# Neutral tract position for rest reset
NEUTRAL_F = [500, 1500, 2500, 3500]
NEUTRAL_B = [120,  150,  250,  350]


# ============================================================
# FIX 3: Z-SPECIFIC VOICED FRACTION
# ============================================================

Z_VOICED_TRACT   = 0.88  # Z: strong voice
ZH_VOICED_TRACT  = 0.82  # ZH: strong voice
V_VOICED_TRACT   = 0.78  # V: clear buzz


# ============================================================
# PLAN PROSODY v7
# Adds: duration caps, rest caps
# ============================================================

def plan_prosody(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL):
    """
    v7: Duration caps on fricatives
    and approximants.
    Rest cap at REST_MAX_MS.
    Everything else identical to v3.
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
            sv = stress_p[si] \
                 if si < len(stress_p) \
                 else 0
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

        # FIX 2: cap fricatives
        if ph in FRIC_MAX_MS:
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
        f0_local   = {2:1.08,1:1.03}.get(
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

        bw_stress = {2:0.75,1:0.90,
                      0:1.10}.get(sv, 1.0)
        bw_pos    = 1.0
        if t_mid > 0.85:
            bw_pos = 1.0 + \
                2.0*(t_mid-0.85)/0.15
        item['bw_mult'] = (bw_stress *
                            bw_pos)
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

        # FIX 4: cap the rest
        rest_ms = min(
            85.0 * bond * dil,
            REST_MAX_MS)
        flat[last_idx]['rest_ms'] = rest_ms

    for item in flat:
        if 'rest_ms' not in item:
            item['rest_ms'] = 0.0

    return flat


# ============================================================
# BUILD TRAJECTORIES v7
# FIX 1: Fixed-ms transition zones.
# FIX 4: Neutral blend during long rests.
# ============================================================

def build_trajectories(phoneme_specs,
                        sr=SR):
    """
    v7: Transition zones are fixed in
    absolute milliseconds via trans_n().
    Only the phoneme body scales with DIL.

    Also: tracks rest_ms per phoneme.
    After a rest longer than 80ms,
    blends F_current toward NEUTRAL_F
    so the next phoneme starts from
    near-neutral rather than from the
    previous extreme.
    """
    if not phoneme_specs:
        return ([np.zeros(1, dtype=DTYPE)]*4,
                [np.zeros(1, dtype=DTYPE)]*4,
                [])

    n_total  = sum(s['n_s']
                   for s in phoneme_specs)
    F_full   = [np.zeros(n_total, dtype=DTYPE)
                for _ in range(4)]
    B_full   = [np.zeros(n_total, dtype=DTYPE)
                for _ in range(4)]
    seg_ends = []

    F_current = list(
        phoneme_specs[0]['F_tgt'])
    B_current = list(
        phoneme_specs[0]['B_tgt'])

    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s     = spec['n_s']
        ph      = spec['ph']
        F_tgt   = spec['F_tgt']
        B_tgt   = spec['B_tgt']
        bw_mult = spec.get('bw_mult', 1.0)
        F_end   = spec.get('F_end', F_tgt)
        is_d    = spec.get(
            'diphthong', False)
        r_f3    = spec.get('r_f3', False)

        # FIX 4: If previous phoneme had
        # a long rest, blend F_current
        # toward neutral before this phoneme
        prev_rest = (
            phoneme_specs[si-1].get(
                'rest_ms', 0.0)
            if si > 0 else 0.0)
        if prev_rest > 80.0:
            # Blend factor: 0 at 80ms, 1 at 280ms
            blend = min(
                (prev_rest - 80.0) / 200.0,
                1.0)
            for fi in range(4):
                F_current[fi] = float(
                    F_current[fi] * (1-blend) +
                    NEUTRAL_F[fi] * blend)
                B_current[fi] = float(
                    B_current[fi] * (1-blend) +
                    NEUTRAL_B[fi] * blend)

        # Next phoneme targets
        if si < len(phoneme_specs)-1:
            F_next   = phoneme_specs[
                si+1]['F_tgt']
            B_next   = phoneme_specs[
                si+1]['B_tgt']
            bw_next  = phoneme_specs[
                si+1].get('bw_mult', 1.0)
        else:
            F_next  = F_end if is_d \
                      else F_tgt
            B_next  = B_tgt
            bw_next = bw_mult

        # FIX 1: fixed-ms transition zones
        n_on  = min(trans_n(ph, sr),
                    n_s // 3)
        n_off = min(trans_n(ph, sr),
                    n_s // 3)
        n_mid = n_s - n_on - n_off
        if n_mid < 1:
            n_mid = 1
            n_on  = (n_s-1)//2
            n_off = n_s-1-n_on

        F_from = list(F_current)
        B_from = list(B_current)

        for fi in range(4):
            f_arr = np.zeros(n_s,
                              dtype=DTYPE)
            if n_on > 0:
                f_arr[:n_on] = np.linspace(
                    float(F_from[fi]),
                    float(F_tgt[fi]),
                    n_on, dtype=DTYPE)
            if n_mid > 0:
                if is_d:
                    nm = int(n_mid*0.72)
                    nh = n_mid-nm
                    if nm > 0:
                        f_arr[n_on:
                              n_on+nm] = \
                            np.linspace(
                                float(F_tgt[fi]),
                                float(F_end[fi]),
                                nm, dtype=DTYPE)
                    if nh > 0:
                        f_arr[n_on+nm:
                              n_on+n_mid] = \
                            float(F_end[fi])
                else:
                    f_arr[n_on:
                          n_on+n_mid] = \
                        float(F_tgt[fi])
            if n_off > 0:
                ff = (float(F_end[fi])
                      if is_d
                      else float(F_tgt[fi]))
                f_arr[n_on+n_mid:] = \
                    np.linspace(
                        ff,
                        float(F_next[fi]),
                        n_off, dtype=DTYPE)
            if r_f3 and fi == 2:
                nd = min(
                    int(0.030*sr), n_s)
                f_arr[:nd] = np.linspace(
                    float(F_from[2]),
                    1690.0, nd, dtype=DTYPE)
                f_arr[nd:] = 1690.0

            F_full[fi][pos:pos+n_s] = f_arr

            # Bandwidth
            b_arr = np.linspace(
                float(B_from[fi]),
                float(B_tgt[fi])*bw_mult,
                n_s, dtype=DTYPE)
            b_arr = np.clip(
                b_arr, 10.0, 1200.0)
            B_full[fi][pos:pos+n_s] = b_arr

        for fi in range(4):
            F_current[fi] = float(
                F_full[fi][pos+n_s-1])
            B_current[fi] = float(
                B_full[fi][pos+n_s-1])

        pos += n_s
        seg_ends.append(pos)

    return F_full, B_full, seg_ends


# ============================================================
# PH SPEC v7
# Passes rest_ms into spec for
# trajectory builder to use.
# ============================================================

def ph_spec_v7(ph, dur_ms,
                pitch=PITCH,
                oq=0.65,
                bw_mult=1.0,
                amp=1.0,
                next_ph=None,
                rest_ms=0.0,
                sr=SR):
    """
    v7 phoneme spec.
    Adds rest_ms so build_trajectories
    can blend toward neutral after
    long rests.
    Coart_frac kept for diphthong
    structure — but transition zones
    are now computed via trans_n(),
    not cf*n_s.
    """
    spec = _ph_spec_v3(
        ph, dur_ms,
        pitch=pitch, oq=oq,
        bw_mult=bw_mult, amp=amp,
        next_ph=next_ph, sr=sr)

    # Embed rest_ms for trajectory builder
    spec['rest_ms'] = rest_ms

    return spec


# ============================================================
# SOURCE BUILDER v7
# FIX 3: Z/ZH/V-specific voiced fractions.
# Context-aware bypass release.
# ============================================================

def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v7:
    FIX 3: Z uses Z_VOICED_TRACT (0.88)
           ZH uses ZH_VOICED_TRACT (0.82)
           V uses V_VOICED_TRACT (0.78)
           Global VOICED_TRACT_FRACTION
           for other voiced fricatives.

    Context-aware bypass release:
    If next phoneme is a vowel/approx,
    bypass fades over full n_off zone,
    not just 8ms.
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
        sh    = f32(np.random.normal(
            0, 1, n_total))
        sh    = f32(lfilter(b, a, sh))
        sh    = f32(np.clip(
            1+0.030*sh, 0.4, 1.6))
        raw_v = raw_v*sh
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
        e = pos+n_s

        # Next phoneme (for bypass release)
        next_ph = (phoneme_specs[si+1]['ph']
                   if si < len(phoneme_specs)-1
                   else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

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
            tract_source[s:e] = \
                voiced_full[s:e]
            byp = _make_bypass_v7(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            # FIX 3: phoneme-specific
            # voiced tract fractions
            if stype == 'fric_v':
                vf = {
                    'Z':  Z_VOICED_TRACT,
                    'ZH': ZH_VOICED_TRACT,
                    'V':  V_VOICED_TRACT,
                }.get(ph, VOICED_TRACT_FRACTION)
                tract_source[s:e] = \
                    voiced_full[s:e] * vf

            byp = _make_bypass_v7(
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


def _make_bypass_v7(ph, n_s, sr=SR,
                     next_is_vowel=False):
    """
    v7 bypass wrapper.
    Context-aware release:
    If next phoneme is vowel/approx,
    extend release to cover full
    n_off zone of this phoneme
    so bypass and tract fade together.
    """
    from voice_physics_v6 import (
        RESONATOR_CFG, BROADBAND_CFG,
        cavity_resonator,
    )

    n_s = int(n_s)

    # Release duration:
    # Standard: 8ms
    # Into vowel/approx: 20ms
    # (covers the transition zone)
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(int(rel_ms/1000.0*sr), n_s//4)
    atk    = min(int(0.005*sr), n_s//4)

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
        from voice_physics_v6 import \
            _CALIBRATED_GAINS
        cfg  = RESONATOR_CFG[ph]
        gain = (_CALIBRATED_GAINS.get(ph,
                cfg['gain'])
                if _CALIBRATED_GAINS
                else cfg['gain'])
        noise     = calibrate(
            f32(np.random.normal(0, 1, n_s)))
        resonated = cavity_resonator(
            noise, cfg['fc'], cfg['bw'],
            sr=sr)
        sib = calibrate(resonated) * gain
        return apply_env(sib)

    elif ph in BROADBAND_CFG:
        from voice_physics_v6 import \
            _CALIBRATED_GAINS
        cfg  = BROADBAND_CFG[ph]
        gain = (_CALIBRATED_GAINS.get(ph,
                cfg['gain'])
                if _CALIBRATED_GAINS
                else cfg['gain'])
        noise = calibrate(
            f32(np.random.normal(0, 1, n_s)))
        try:
            b, a  = safe_hp(
                cfg['hp_fc'], sr)
            broad = f32(lfilter(b, a, noise))
        except:
            broad = noise.copy()
        sib = calibrate(broad) * gain
        return apply_env(sib)

    else:
        return f32(np.zeros(n_s))


# ============================================================
# PHRASE SYNTHESIS v7
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v7: All four fixes active.
    Fixed-ms transitions.
    Fricative duration caps.
    Z/ZH/V voiced contrast raised.
    Rest cap + neutral tract blend.
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

    tract_src, bypass_segs = \
        build_source_and_bypass(specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos+len(byp), n_total)
        n = e - pos
        out[pos:e] += byp[:n]

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

    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

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
    print("VOICE PHYSICS v7")
    print("Transition timing + voicing fixes.")
    print()
    print("  FIX 1: Fixed-ms transitions")
    print("         Bodies stretch. Edges don't.")
    print("  FIX 2: Fricative duration cap")
    print("         S max 180ms. Z max 180ms.")
    print("  FIX 3: Z/ZH/V voiced contrast")
    print("         Z voiced tract = 0.88")
    print("  FIX 4: Rest cap + neutral blend")
    print("         Rest max 240ms.")
    print("         Tract resets between words.")
    print("="*60)
    print()

    # Calibrate gains first
    print("  Calibrating gains...")
    recalibrate_gains(sr=SR)
    print()

    # Primary test — the reported phrase
    print("  The voice was always here...")
    seg = synth_phrase(
        [('the',    ['DH', 'AH']),
         ('voice',  ['V', 'OY', 'S']),
         ('was',    ['W', 'AH', 'Z']),
         ('always', ['AA', 'L', 'W',
                      'EH', 'Z']),
         ('here',   ['H', 'IH', 'R'])],
        punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_always_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_always_here.wav")

    # Original diagnostic phrase too
    print()
    print("  The voice was already here...")
    seg = synth_phrase(
        [('the',     ['DH', 'AH']),
         ('voice',   ['V', 'OY', 'S']),
         ('was',     ['W', 'AH', 'Z']),
         ('already', ['AA', 'L', 'R',
                       'EH', 'D', 'IY']),
         ('here',    ['H', 'IH', 'R'])],
        punctuation='.',
        pitch_base=PITCH)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        apply_room(seg, rt60=1.5, dr=0.50))
    print("    the_voice_was_already_here.wav")

    # S vs Z contrast isolated
    print()
    print("  S/Z contrast...")
    for phs, label in [
        (['AA', 'S'],  'S_isolated'),
        (['AA', 'Z'],  'Z_isolated'),
        (['AA', 'S', 'AH', 'Z'], 'S_then_Z'),
    ]:
        seg = synth_phrase(
            [('test', phs)],
            pitch_base=PITCH)
        write_wav(
            f"output_play/contrast_{label}.wav",
            apply_room(seg, rt60=1.2,
                        dr=0.60))
        print(f"    contrast_{label}.wav")

    # Sentence types
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            [('the',   ['DH', 'AH']),
             ('voice', ['V', 'OY', 'S']),
             ('was',   ['W', 'AH', 'Z']),
             ('always',['AA', 'L', 'W',
                         'EH', 'Z']),
             ('here',  ['H', 'IH', 'R'])],
            punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            apply_room(
                seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Additional phrases
    print()
    print("  Phrases...")
    for label, words, punct in [
        ('still_here',
         [('still', ['S','T','IH','L']),
          ('here',  ['H','IH','R'])], '.'),
        ('water_home',
         [('water', ['W','AA','T','ER']),
          ('home',  ['H','OW','M'])], '.'),
        ('always_open',
         [('always', ['AA','L','W',
                       'EH','Z']),
          ('open',   ['OH','P','EH','N'])],
         '.'),
        ('not_yet',
         [('not', ['N','AA','T']),
          ('yet', ['Y','EH','T'])], '.'),
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
    print("  PRIMARY — the new phrase:")
    print("  afplay output_play/"
          "the_voice_was_always_here.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  'voice' — does it sound like")
    print("  one syllable now? (not 'voi-ce')")
    print()
    print("  'was' — does Z have a distinct")
    print("  buzz? Not just more S?")
    print()
    print("  'always' — does Z end cleanly")
    print("  without a trailing 's'?")
    print()
    print("  'here' — does it start cleanly?")
    print("  No 'teh' before it?")
    print()
    print("  S vs Z contrast:")
    print("  afplay output_play/"
          "contrast_S_then_Z.wav")
    print("  S: clean hiss, no voice")
    print("  Z: hiss WITH buzz underneath")
    print("  Should be clearly different.")
    print()
