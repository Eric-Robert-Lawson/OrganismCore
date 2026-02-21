"""
VOICE PHYSICS v10 — REVISED
February 2026

ONSET DIAGNOSTIC RESULTS:

  DH: centroid=770Hz  (target 1800-5000Hz) ✗
      rms_ratio=1.008 (target ≤ 0.60)      ✗
      periodicity=0.296                     ✓

  H:  centroid=760Hz  (target 800-2500Hz)  ✗
      peak_prominence=44.73 (target ≤ 3.0) ✗
      periodicity=0.15                     ✓

  S:  timing=late                          ✓
  Z:  no_sibilance                         ✗

THREE ROOT CAUSES:

  DH: centroid=770Hz means F1=270Hz resonator
      is dominating even at low voiced level.
      The resonator amplifies 270Hz signal
      regardless of input level.
      Even voiced_fraction=0.01 through
      F1=270Hz produces a 270Hz spike.
      FIX: DH onset routes through a
      WIDENED tract (high bandwidth =
      low Q = no sharp resonance).
      Or: DH onset bypasses tract entirely.
      Choice: bypass tract for first
      DH_TRACT_BYPASS_MS, then fade in.

  H:  peak_prominence=44.73 means the
      4-resonator tract is ringing sharply.
      H_NEUTRAL_F[0]=450Hz at BW=120Hz
      gives Q=3.75. Any noise input
      produces a 44× spike at 450Hz.
      This is not aspiration. It is
      a resonated tone masquerading
      as aspiration.
      FIX: H aspiration source bypasses
      the tract entirely.
      H source goes DIRECTLY to output.
      Not through any resonator.
      The tract is silent during H.
      The following vowel's resonators
      fade in at the IH onset.

  Z:  no_sibilance means calibrated
      bypass gain for Z is near zero,
      or the bypass signal never exceeds
      0.25 normalized amplitude.
      FIX: Z bypass gain floor = 0.45
      regardless of calibration result.
      If calibration produces gain < 0.45,
      use 0.45.

Import chain:
  v10 → v9 → v8 → v7 → v6 → v5 → v4 → v3
"""

from voice_physics_v9 import (
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
    VOWEL_PHONEMES, DIPHTHONG_PHONEMES,
    VOWEL_MAX_MS, DIPHTHONG_MAX_MS,
    APPROX_MAX_MS, FRIC_MAX_MS,
    FINAL_FRIC_MAX_MS,
    DH_MAX_MS, H_MAX_MS,
    H_ASPIRATION_GAIN,
    build_trajectories,
    ph_spec_v9,
    plan_prosody,
    get_calibrated_gains_v8,
    recalibrate_gains_v8,
    RESONATOR_CFG, BROADBAND_CFG,
    cavity_resonator,
    VOICED_FRICS, FRIC_VOICED_TRACT,
    make_bypass_v9,
)
import numpy as np
from scipy.signal import lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# FIX 1: DH TRACT BYPASS AT ONSET
#
# Problem: centroid=770Hz even with fade-in.
# Even a tiny voiced signal through the
# F1=270Hz resonator produces a 270Hz spike.
# The resonator amplifies regardless of level.
#
# Fix: During DH_TRACT_BYPASS_MS,
# the DH source does NOT go through the tract.
# It goes directly to output via the bypass path.
# The bypass carries the dental friction.
# The tract is silent.
# After DH_TRACT_BYPASS_MS, voiced signal
# fades into the tract normally.
#
# What the ear hears:
#   t=0:           dental friction (bypass only)
#   t=25ms onward: dental friction + growing buzz
#   t=45ms onward: voiced dental consonant
#   → "the" not "ea-the"
# ============================================================

DH_TRACT_BYPASS_MS  = 25   # ms of tract silence at onset
DH_VOICED_FRACTION  = 0.30 # target voiced fraction at body
# Voiced fades IN from 0 starting at DH_TRACT_BYPASS_MS


# ============================================================
# FIX 2: H BYPASSES TRACT ENTIRELY
#
# Problem: peak_prominence=44.73.
# The 4-resonator tract rings sharply
# at its lowest formant frequency.
# Any noise input, at any level,
# produces a resonant spike.
# There is no way to route aspiration
# through a resonator bank and get
# flat broadband output.
# The resonator is the wrong tool for H.
#
# Fix: H aspiration goes DIRECTLY to output.
# tract_source[H segment] = 0.
# H aspiration is added as a bypass segment,
# identical mechanism to fricative bypass.
#
# The following vowel (IH, OW, etc.)
# begins at its own onset with its own
# formant targets. The tract starts from
# neutral or the H formant position
# at the vowel onset — which is correct
# because the tract was NOT active during H.
#
# Result: H sounds like pure aspiration
# (broadband breath), not a resonated tone.
# The "CH" prefix disappears because
# there is no palatal resonance at H onset.
# ============================================================

H_BYPASS_GAIN     = 0.55  # output level of H aspiration
H_BYPASS_HP_HZ    = 150   # high-pass to remove sub-bass
H_BYPASS_LP_HZ    = 7000  # low-pass to remove ultrasonic


# ============================================================
# FIX 3: Z BYPASS GAIN FLOOR
#
# Problem: Z sibilance never rises above 0.25.
# Calibration is producing a near-zero gain.
# Or the resonator output is being suppressed.
#
# Fix: Z bypass gain has a hard floor.
# If calibrated gain < Z_BYPASS_GAIN_FLOOR,
# use the floor value instead.
# ============================================================

Z_BYPASS_GAIN_FLOOR = 0.45
# Also apply floor to ZH:
ZH_BYPASS_GAIN_FLOOR = 0.35


# ============================================================
# BYPASS GENERATOR v10
# Adds gain floor for Z/ZH.
# H uses a separate function (see below).
# ============================================================

def make_bypass_v10(ph, n_s, sr=SR,
                     next_is_vowel=False,
                     onset_delay=0):
    """
    v10 bypass.
    Identical to v9 but with gain floor
    for Z and ZH.
    onset_delay: bypass starts at this
    sample offset (rest is zero).
    """
    gains = get_calibrated_gains_v8(sr=sr)
    gain  = gains.get(ph, None)

    # FIX 3: Z/ZH gain floor
    if ph == 'Z':
        if gain is None or gain < Z_BYPASS_GAIN_FLOOR:
            gain = Z_BYPASS_GAIN_FLOOR
    elif ph == 'ZH':
        if gain is None or gain < ZH_BYPASS_GAIN_FLOOR:
            gain = ZH_BYPASS_GAIN_FLOOR

    n_s        = int(n_s)
    onset_delay = max(0, int(onset_delay))
    if onset_delay >= n_s:
        return f32(np.zeros(n_s))

    n_eff = n_s - onset_delay
    rel_ms = 20 if next_is_vowel else 8
    rel    = min(int(rel_ms/1000.0*sr), n_eff//4)
    atk    = min(int(0.005*sr), n_eff//4)

    def apply_env(sig):
        env = f32(np.ones(n_eff))
        if atk > 0 and atk < n_eff:
            env[:atk] = f32(np.linspace(0,1,atk))
        if rel > 0:
            env[-rel:] = f32(np.linspace(1,0,rel))
        return f32(sig * env)

    raw = np.zeros(n_s, dtype=DTYPE)

    if ph in RESONATOR_CFG:
        cfg  = RESONATOR_CFG[ph]
        g    = gain if gain is not None \
               else cfg['gain']
        noise     = calibrate(
            f32(np.random.normal(0,1,n_eff)))
        resonated = cavity_resonator(
            noise, cfg['fc'], cfg['bw'], sr=sr)
        sib = calibrate(resonated) * g
        raw[onset_delay:] = apply_env(sib)

    elif ph in BROADBAND_CFG:
        cfg  = BROADBAND_CFG[ph]
        g    = gain if gain is not None \
               else cfg['gain']
        noise = calibrate(
            f32(np.random.normal(0,1,n_eff)))
        try:
            b, a  = safe_hp(cfg['hp_fc'], sr)
            broad = f32(lfilter(b,a,noise))
        except:
            broad = noise.copy()
        sib = calibrate(broad) * g
        raw[onset_delay:] = apply_env(sib)

    return f32(raw)


def make_h_bypass(n_s, sr=SR,
                   next_is_vowel=False):
    """
    FIX 2: H aspiration bypass.
    Goes directly to output, never through tract.

    Broadband aspiration:
      HP at H_BYPASS_HP_HZ (removes sub-bass)
      LP at H_BYPASS_LP_HZ (removes ultrasonic)
      No resonator. No formant shaping.
      Flat broadband breath.

    Envelope:
      Onset: 8ms fade in (from 0.2 to 1.0)
             H always starts breathy, not silent.
      Body:  flat
      Offset: 20ms fade out if into vowel,
              else 12ms.
              Fade gives natural vowel onset.
    """
    n_s = int(n_s)
    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))

    # Broadband shaping
    try:
        b, a  = safe_hp(H_BYPASS_HP_HZ, sr)
        broad = f32(lfilter(b, a, noise))
    except:
        broad = noise.copy()

    try:
        # scipy lp — use butter directly
        from scipy.signal import butter
        nyq  = sr * 0.5
        wn   = min(H_BYPASS_LP_HZ / nyq, 0.98)
        b, a = butter(2, wn, btype='low')
        broad = f32(lfilter(b, a, broad))
    except:
        pass

    broad = calibrate(broad) * H_BYPASS_GAIN

    # Envelope
    atk_ms = 8
    rel_ms = 20 if next_is_vowel else 12
    atk    = min(int(atk_ms/1000.0*sr), n_s//4)
    rel    = min(int(rel_ms/1000.0*sr), n_s//4)

    env = f32(np.ones(n_s))
    if atk > 0:
        # Start at 0.2 (H is never fully silent
        # at onset — there is always some breath)
        env[:atk] = f32(np.linspace(0.2, 1.0, atk))
    if rel > 0:
        env[-rel:] = f32(np.linspace(1.0, 0.0, rel))

    return f32(broad * env)


# ============================================================
# TRAJECTORY BUILDER v10
#
# When H is present:
# The tract is silent during H (tract_source=0).
# The tract still has formant trajectories
# but they don't matter for H because
# the H source does not go through the tract.
#
# HOWEVER: the tract state at the START of IH
# must be reasonable, not at whatever H's
# F_tgt was. Otherwise IH has a glitch
# at its onset as the resonators ring up
# from the H position.
#
# Fix: for H phonemes, set F_tgt and F_end
# to NEUTRAL_F. The tract "rests" at neutral
# during H. When IH begins, the tract
# starts from neutral (or from the blend
# toward IH F_tgt). Natural onset for IH.
# ============================================================

def build_trajectories_v10(phoneme_specs, sr=SR):
    """
    v10: H phonemes use NEUTRAL_F as their
    formant target. This prevents the tract
    from resonating strangely during H
    even though H source bypasses the tract.
    It also gives IH a clean starting position.
    All other phonemes unchanged.
    """
    # Temporarily override H specs
    # to use neutral formants
    patched_specs = []
    for spec in phoneme_specs:
        if spec['ph'] == 'H':
            import copy
            s = copy.copy(spec)
            s['F_tgt'] = list(NEUTRAL_F)
            s['B_tgt'] = list(NEUTRAL_B)
            if 'F_end' in s:
                s['F_end'] = list(NEUTRAL_F)
            patched_specs.append(s)
        else:
            patched_specs.append(spec)

    return build_trajectories(
        patched_specs, sr=sr)


# ============================================================
# SOURCE BUILDER v10
# ============================================================

def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v10:
    FIX 1: DH — tract silent for first
            DH_TRACT_BYPASS_MS,
            voiced fades in after.
    FIX 2: H  — tract source = 0,
            H goes to bypass as broadband
            aspiration (no resonators).
    FIX 3: Z  — bypass gain floor 0.45.
    FIX C: sibilant onset delay = full n_on.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # F0/oq trajectories
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
        p  += f0*(1+np.random.normal(0,0.005))*T
        if p >= 1.0: p -= 1.0
        raw_v[i] = (
            (p/oq_)*(2-p/oq_) if p < oq_
            else 1-(p-oq_)/(1-oq_+1e-9))
    raw_v = f32(np.diff(raw_v, prepend=raw_v[0]))
    try:
        b,a   = safe_lp(20, sr)
        sh_   = f32(np.random.normal(0,1,n_total))
        sh_   = f32(lfilter(b,a,sh_))
        sh_   = f32(np.clip(1+0.030*sh_,0.4,1.6))
        raw_v = raw_v*sh_
    except:
        pass
    asp_src = f32(np.random.normal(0,0.020,n_total))
    try:
        b,a     = safe_bp(400,2200,sr)
        asp_src = f32(lfilter(b,a,asp_src))
    except:
        asp_src = f32(np.zeros(n_total))
    raw_v       = raw_v + asp_src
    voiced_full = calibrate(raw_v)
    noise_full  = calibrate(
        f32(np.random.normal(0,1,n_total)))

    VOWELS_AND_APPROX = set(
        'AA AE AH AO AW AY EH ER IH IY '
        'OH OW OY UH UW L R W Y M N NG'.split())

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

        next_ph = (phoneme_specs[si+1]['ph']
                   if si < len(phoneme_specs)-1
                   else None)
        next_is_vowel = (
            next_ph in VOWELS_AND_APPROX)

        n_on  = min(trans_n(ph, sr), n_s//3)
        n_off = min(trans_n(ph, sr), n_s//3)
        n_body = max(0, n_s - n_on - n_off)

        if stype == 'voiced':
            tract_source[s:e] = voiced_full[s:e]

        elif stype == 'h':
            # FIX 2: H tract source = 0.
            # H goes entirely through bypass.
            # tract_source[s:e] stays zero.
            byp = make_h_bypass(
                n_s, sr,
                next_is_vowel=next_is_vowel)
            bypass_segs.append((s, byp))

        elif stype == 'dh':
            # FIX 1: DH tract bypass at onset.
            #
            # tract_source during first n_dh_bypass
            # samples = 0.
            # After n_dh_bypass, voiced fades in
            # from 0 → DH_VOICED_FRACTION
            # over the remaining body.
            #
            # Bypass: dental friction for full
            # DH duration, onset_delay = 0
            # (bypass starts immediately —
            # it IS the DH onset).

            n_silent = min(n_dh_bypass, n_s)
            n_remain = n_s - n_silent

            if n_remain > 0:
                voiced_amp = np.zeros(
                    n_s, dtype=DTYPE)
                voiced_amp[n_silent:] = f32(
                    np.linspace(
                        0.0,
                        DH_VOICED_FRACTION,
                        n_remain))
                # Fade out over n_off zone
                fade_start = n_on + n_body
                if n_off > 0 and \
                   fade_start < n_s:
                    current = float(
                        voiced_amp[
                            min(fade_start,
                                n_s-1)])
                    voiced_amp[fade_start:] = \
                        f32(np.linspace(
                            current,
                            0.0, n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(voiced_amp)

            # Bypass starts at t=0 for DH
            # (friction is the onset)
            byp = make_bypass_v10(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=0)
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
                        np.linspace(1.0,0.0,n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(amp) * vf

            # Full n_on delay (FIX C from v9)
            onset_delay = n_on
            byp = make_bypass_v10(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=onset_delay)
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
                    voiced_full[s:s+clos_n]*0.055
            if burst_n > 0:
                bs = clos_n
                be = bs + burst_n
                if be <= n_s:
                    burst = noise_full[
                        s+bs:s+be].copy()
                    try:
                        b,a   = safe_hp(bhp,sr)
                        burst = f32(
                            lfilter(b,a,burst))
                    except:
                        pass
                    benv = f32(np.exp(
                        -np.arange(burst_n)/
                        burst_n*20))
                    tract_source[s+bs:s+be] = \
                        burst*benv*bamp
            vot_s = clos_n + burst_n
            vot_e = vot_s  + vot_n
            if vot_n > 0 and vot_e <= n_s:
                ne2 = f32(np.linspace(1,0,vot_n))
                ve2 = 1.0 - ne2
                tract_source[s+vot_s:s+vot_e] = (
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
# PHRASE SYNTHESIS v10
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v10: Three onset fixes.
    DH tract bypassed at onset.
    H bypasses tract entirely.
    Z gain floor enforced.
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
        word_final = item.get('word_final', False)
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
    # (H uses neutral formants)
    F_full, B_full, _ = \
        build_trajectories_v10(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    tract_src, bypass_segs = \
        build_source_and_bypass(specs, sr=sr)

    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    for pos, byp in bypass_segs:
        e = min(pos+len(byp), n_total)
        n = e-pos
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
            af,abw = NASAL_AF[ph]
            seg    = out[pos:pos+n_s].copy()
            anti   = np.zeros(n_s, dtype=DTYPE)
            y1=y2=0.0
            for i in range(n_s):
                a2 = -np.exp(-2*np.pi*abw*T)
                a1 =  2*np.exp(-np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0 = 1.0-a1-a2
                y  = b0*float(seg[i])+a1*y1+a2*y2
                y2=y1; y1=y; anti[i]=y
            out[pos:pos+n_s] = \
                seg - f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            hg = int(0.012*sr)
            if hg>0 and hg<n_s:
                out[pos+n_s-hg:pos+n_s]=0.0
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
    if atk>0 and atk<n_total:
        env[:atk]  = f32(np.linspace(0,1,atk))
    if rel>0:
        env[-rel:] = f32(np.linspace(1,0,rel))
    out = out * f32(amp_env) * env

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
    p95   = np.percentile(np.abs(final), 95)
    if p95 > 1e-8:
        final = final/p95*0.88
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
        sig = apply_room(sig,rt60=rt60,dr=dr,sr=sr)
    write_wav(f"output_play/{name}.wav", sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v10")
    print("Three onset fixes from diagnostic.")
    print()
    print("  FIX 1: DH tract silent at onset")
    print("         First 25ms: bypass only.")
    print("         Resonator cannot spike")
    print("         what it does not receive.")
    print("         Dental friction IS onset.")
    print()
    print("  FIX 2: H bypasses tract entirely")
    print("         H source never enters tract.")
    print("         No resonator. No spike.")
    print("         Pure broadband aspiration.")
    print("         Tract rests at neutral.")
    print("         IH begins from neutral.")
    print()
    print("  FIX 3: Z bypass gain floor 0.45")
    print("         Z sibilance was zero.")
    print("         Floor prevents calibration")
    print("         from zeroing out Z.")
    print("="*60)
    print()

    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    print("  Running onset diagnostic...")
    print()
    from onset_diagnostic import run_onset_diagnostic
    results, n_pass, n_fail = \
        run_onset_diagnostic(
            synth_phrase, PITCH, sr=SR)
    print()

    if n_fail > 0:
        print("  Onset diagnostic still failing.")
        print("  Constants to adjust:")
        print()
        dh_r = results.get('DH', {})
        if not all(v.get('pass', True)
                   for v in dh_r.values()):
            print("  DH still failing:")
            print("  → Increase DH_TRACT_BYPASS_MS")
            print("    (currently 25ms)")
            print()
        h_r = results.get('H', {})
        if not all(v.get('pass', True)
                   for v in h_r.values()):
            print("  H still failing:")
            print("  → Check make_h_bypass is")
            print("    being called (not make_bypass)")
            print("  → Reduce H_BYPASS_GAIN if")
            print("    prominence still high")
            print()
        z_r = results.get('Z_timing', {})
        if not z_r.get('pass', True):
            print("  Z timing still failing:")
            print("  → Increase Z_BYPASS_GAIN_FLOOR")
            print("    (currently 0.45)")
            print()

    # Primary phrase
    print("  Primary phrase...")
    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V',  'OY', 'S']),
        ('was',     ['W',  'AH', 'Z']),
        ('already', ['AA', 'L',  'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H',  'IH', 'R']),
    ]
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
    for label, words, note in [
        ('test_the',
         [('the', ['DH','AH'])],
         'no ea-prefix'),
        ('test_here',
         [('here', ['H','IH','R'])],
         'breathy, no CH-prefix'),
        ('test_was',
         [('was', ['W','AH','Z'])],
         'Z distinct'),
        ('test_voice',
         [('voice', ['V','OY','S'])],
         'S clean after OY'),
        ('test_this_is_here',
         [('this', ['DH','IH','S']),
          ('is',   ['IH','Z']),
          ('here', ['H','IH','R'])],
         'DH+H in phrase'),
    ]:
        seg = synth_phrase(
            words, pitch_base=PITCH)
        write_wav(
            f"output_play/{label}.wav",
            apply_room(seg, rt60=1.2, dr=0.55))
        print(f"    {label}.wav  ({note})")

    print()
    print("  Sentence types...")
    for punct, label in [
            ('.','statement'),
            ('?','question'),
            ('!','exclaim')]:
        seg = synth_phrase(
            PHRASE, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/the_voice_{label}.wav",
            apply_room(seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    print()
    print("  Additional phrases...")
    for label, words, punct in [
        ('water_home',
         [('water',['W','AA','T','ER']),
          ('home', ['H','OW','M'])],'.'),
        ('still_here',
         [('still',['S','T','IH','L']),
          ('here', ['H','IH','R'])],'.'),
        ('here_and_there',
         [('here', ['H','IH','R']),
          ('and',  ['AE','N','D']),
          ('there',['DH','EH','R'])],'.'),
    ]:
        seg = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/phrase_{label}.wav",
            apply_room(seg, rt60=1.6, dr=0.48))
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  Onset diagnostic: "
          f"{n_pass}/{n_pass+n_fail} passing")
    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  afplay output_play/test_the.wav")
    print("  afplay output_play/test_here.wav")
    print("  afplay output_play/test_was.wav")
    print("  afplay output_play/test_voice.wav")
    print()
