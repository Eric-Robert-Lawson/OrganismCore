"""
VOICE PHYSICS v9
February 2026

FOUR CONSONANT IDENTITY FIXES.

Perceptual report from v8:

  "the"  → "ea-the"   (onset vowel before DH)
  "here" → "CH-here"  (affricate percept before H)
  "waS"  → dragged    (S trailing the vowel)
  "voiCe"→ dragged    (S/OY boundary smeared)

Root cause: consonants too voiced,
too long, bypass onset misaligned.

FIX 1: DH — voiced fraction 0.70 → 0.30
  DH was spending 160ms with voiced_full
  at 0.70 level through dental formants.
  [270, 900, ...] formants + strong voicing
  = a schwa-like vowel prefix.
  Reduce voiced fraction.
  Enforce DH_MAX_MS = 75ms.

FIX 2: H — pure aspiration model
  H was: 12% noise, crossfade, 88% modal voiced.
  88% modal voiced through IH formants
  = a quiet IH vowel for 210ms.
  Ear hears: breathy-IH → IH = "CH" + vowel.
  Fix: H = 100% aspirated turbulence.
  Zero modal voicing during H body.
  Pure aspiration noise through
  next-vowel formants.
  Duration cap: H_MAX_MS = 75ms.
  Breathiness fraction raised to 30%
  (was 12%).

FIX 3: WORD-FINAL SIBILANT CAP
  Word-final S/Z/SH/ZH before a rest:
  max 120ms (not 180ms).
  The sibilant ends cleanly.
  The rest begins.
  No trailing hiss.

FIX 4: BYPASS ONSET DELAY FOR TRANSITIONS
  Bypass was starting at t=0 of phoneme
  (with 5ms attack).
  Tract was still at preceding vowel position.
  Vowel formants + active sibilance = smear.
  Fix: bypass onset delayed by n_on//2.
  Bypass starts when tract is already
  halfway through its transition.
  The sibilance arrives with the
  consonant, not before it.

Import chain:
  v9 → v8 → v7 → v6 → v5 → v4 → v3
"""

from voice_physics_v8 import (
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
    build_trajectories,
    ph_spec_v7,
    get_calibrated_gains_v8,
    recalibrate_gains_v8,
    make_bypass_v8,
    RESONATOR_CFG, BROADBAND_CFG,
    cavity_resonator,
    VOICED_FRICS, FRIC_VOICED_TRACT,
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
# FIX 1: DH VOICED FRACTION
# ============================================================

DH_VOICED_FRACTION = 0.30
# Was 0.70. Dental friction is identity.
# Voicing confirms it is DH not TH.
# But voicing must not dominate.

DH_MAX_MS = 75
# DH in function words is brief.
# "the", "this", "that" —
# the DH is a quick dental gesture.
# 75ms is already generous at any tempo.


# ============================================================
# FIX 2: H PURE ASPIRATION MODEL
# ============================================================

H_MAX_MS         = 75
# H is a transitional glide.
# It has no body to stretch.
# 75ms is enough at any tempo.

H_NOISE_FRACTION = 0.30
# Fraction of H that is pure turbulence
# (the aspirated onset).
# Was 0.12. Raised so the breathy
# character is clearly heard.

# H modal voiced fraction:
H_VOICED_FRACTION = 0.0
# ZERO. H is never modal voiced.
# The periodicity of the following vowel
# begins at the vowel onset, not during H.
# H = aspiration only.

H_ASPIRATION_GAIN = 0.55
# Amplitude of aspiration noise
# relative to calibrated level.
# Enough to be heard as breathy.
# Not so loud it sounds like SH.


# ============================================================
# FIX 3: WORD-FINAL SIBILANT CAP
# ============================================================

FINAL_FRIC_MAX_MS = {
    'S':  120, 'Z':  120,
    'SH': 140, 'ZH': 140,
    'F':  100, 'V':  100,
    'TH': 110, 'DH':  75,
}
# These are the caps for phonemes
# that immediately precede a syntactic rest
# (i.e. are word-final).
# Internal sibilants keep the
# existing FRIC_MAX_MS caps.


# ============================================================
# FIX 4: BYPASS ONSET DELAY
#
# Bypass was starting at t=0.
# Tract was still at preceding vowel.
# Vowel + sibilance = smear.
#
# Delay bypass by n_on // 2 samples.
# This aligns bypass onset with
# the midpoint of the tract transition.
# The sibilance arrives WITH the
# consonant articulation, not before it.
# ============================================================

# Phonemes that get onset delay
BYPASS_ONSET_DELAY_PHS = {
    'S', 'Z', 'SH', 'ZH', 'F', 'V',
    'TH', 'DH',
}


def make_bypass_v9(ph, n_s, sr=SR,
                    next_is_vowel=False,
                    onset_delay=0):
    """
    v9 bypass generator.
    Adds onset_delay: bypass starts
    onset_delay samples into the phoneme.
    The leading samples are zero.
    Bypass reaches full level at
    5ms after onset_delay.
    """
    gains = get_calibrated_gains_v8(sr=sr)
    gain  = gains.get(ph, None)

    n_s        = int(n_s)
    onset_delay = max(0, int(onset_delay))
    if onset_delay >= n_s:
        return f32(np.zeros(n_s))

    # Effective segment length after delay
    n_eff = n_s - onset_delay

    rel_ms  = 20 if next_is_vowel else 8
    rel     = min(int(rel_ms/1000.0*sr),
                  n_eff // 4)
    atk     = min(int(0.005*sr), n_eff // 4)

    def apply_env(sig):
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
        cfg = RESONATOR_CFG[ph]
        g   = (gain if gain is not None
               else cfg['gain'])
        noise     = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        resonated = cavity_resonator(
            noise, cfg['fc'], cfg['bw'],
            sr=sr)
        sib = calibrate(resonated) * g
        raw[onset_delay:] = apply_env(sib)

    elif ph in BROADBAND_CFG:
        cfg = BROADBAND_CFG[ph]
        g   = (gain if gain is not None
               else cfg['gain'])
        noise = calibrate(
            f32(np.random.normal(0, 1, n_eff)))
        try:
            b, a  = safe_hp(cfg['hp_fc'], sr)
            broad = f32(lfilter(b, a, noise))
        except:
            broad = noise.copy()
        sib = calibrate(broad) * g
        raw[onset_delay:] = apply_env(sib)

    return f32(raw)


# ============================================================
# PLAN PROSODY v9
# Adds: DH cap, H cap, word-final fric cap.
# ============================================================

def plan_prosody(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL):
    """
    v9 prosody planner.
    Adds DH_MAX_MS, H_MAX_MS caps.
    Word-final sibilants capped at
    FINAL_FRIC_MAX_MS values.
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

    # Identify word-final phoneme indices
    last_ph_of_word = {}
    for i, item in enumerate(flat):
        last_ph_of_word[
            item['word_idx']] = i
    word_final_indices = set(
        last_ph_of_word.values())

    # First pass: durations with all caps
    for i, item in enumerate(flat):
        ph  = item['ph']
        sv  = item['stress']
        d   = PHON_DUR_BASE.get(ph, 80)
        d  *= DUR_SCALE.get(sv, 1.0)
        d  *= dil

        is_word_final = (i in word_final_indices)
        item['word_final'] = is_word_final

        # FIX 2: H cap
        if ph == 'H':
            d = min(d, H_MAX_MS)
        # FIX 1: DH cap
        elif ph == 'DH':
            d = min(d, DH_MAX_MS)
        # FIX 3: word-final fric cap
        elif ph in FINAL_FRIC_MAX_MS \
                and is_word_final:
            d = min(d, FINAL_FRIC_MAX_MS[ph])
        # Standard fric cap (internal)
        elif ph in FRIC_MAX_MS:
            d = min(d, FRIC_MAX_MS[ph])
        # Vowel caps
        elif ph in DIPHTHONG_PHONEMES:
            d = min(d, DIPHTHONG_MAX_MS.get(
                sv, 360))
        elif ph in VOWEL_PHONEMES:
            d = min(d, VOWEL_MAX_MS.get(
                sv, 300))
        # Approximant / nasal caps
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
            bt_p = (t_mid - 0.80) / 0.20
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

    # Third pass: rests
    n_words = len(words_phonemes)
    for wi in range(n_words-1):
        last_idx = last_ph_of_word[wi]
        w_this   = words_phonemes[wi][0].lower()
        w_next   = words_phonemes[wi+1][0].lower()
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
# SOURCE BUILDER v9
# FIX 1: DH voiced fraction 0.30
# FIX 2: H = pure aspiration
# FIX 4: bypass onset delay
# ============================================================

def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v9 source builder.
    FIX 1: DH voiced fraction = 0.30.
    FIX 2: H = pure aspiration, 0 modal voice.
    FIX 4: bypass onset delayed by n_on//2.
    """
    n_total = sum(
        s['n_s'] for s in phoneme_specs)

    # F0 and oq trajectories
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

    # Rosenberg pulse voiced source
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
    asp_src = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b, a    = safe_bp(400, 2200, sr)
        asp_src = f32(lfilter(b, a, asp_src))
    except:
        asp_src = f32(np.zeros(n_total))
    raw_v       = raw_v + asp_src
    voiced_full = calibrate(raw_v)

    # Aspiration noise source (for H)
    asp_noise = calibrate(
        f32(np.random.normal(0, 1, n_total)))
    try:
        b, a      = safe_bp(200, 8000, sr)
        asp_noise = f32(
            lfilter(b, a, asp_noise))
        asp_noise = calibrate(asp_noise)
    except:
        pass

    noise_full = calibrate(
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
        is_word_final = spec.get(
            'word_final', False)

        # Transition zone (for bypass delay)
        n_on  = min(trans_n(ph, sr), n_s // 3)
        n_off = min(trans_n(ph, sr), n_s // 3)
        n_body = n_s - n_on - n_off

        if stype == 'voiced':
            tract_source[s:e] = \
                voiced_full[s:e]

        elif stype == 'h':
            # FIX 2: H = pure aspiration
            # No modal voicing.
            # Aspiration noise for full duration,
            # shaped by following vowel formants
            # via the tract.
            n_asp = int(n_s * H_NOISE_FRACTION)
            n_asp = max(n_asp, min(
                int(0.025*sr), n_s))

            # Full aspiration envelope
            asp_env = np.ones(n_s, dtype=DTYPE)
            # Fade in over first 8ms
            n_fi = min(int(0.008*sr), n_s//4)
            if n_fi > 0:
                asp_env[:n_fi] = np.linspace(
                    0.3, 1.0, n_fi)
            # Fade out over last 12ms
            n_fo = min(int(0.012*sr), n_s//4)
            if n_fo > 0:
                asp_env[-n_fo:] = np.linspace(
                    1.0, 0.0, n_fo)

            # Pure aspiration: no modal voice
            tract_source[s:e] = (
                asp_noise[s:e] *
                f32(asp_env) *
                H_ASPIRATION_GAIN)

        elif stype == 'dh':
            # FIX 1: DH voiced fraction 0.30
            # Fade voicing over n_off zone
            vf  = DH_VOICED_FRACTION
            amp = np.ones(n_s, dtype=DTYPE)
            if n_off > 0 and n_body > 0:
                amp[n_body + n_on:] = f32(
                    np.linspace(1.0, 0.0,
                                 n_off))
            tract_source[s:e] = \
                voiced_full[s:e] * \
                f32(amp) * vf

            # FIX 4: bypass onset delay
            onset_delay = n_on // 2
            byp = make_bypass_v9(
                'DH', n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=onset_delay)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                vf  = FRIC_VOICED_TRACT.get(
                    ph, VOICED_TRACT_FRACTION)
                amp = np.ones(n_s, dtype=DTYPE)
                if n_off > 0 and n_body > 0:
                    amp[n_on + n_body:] = f32(
                        np.linspace(
                            1.0, 0.0, n_off))
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    f32(amp) * vf

            # FIX 4: bypass onset delay
            # Delay = half the transition time.
            # Bypass starts when tract is
            # 50% of the way to fricative position.
            onset_delay = n_on // 2
            byp = make_bypass_v9(
                ph, n_s, sr,
                next_is_vowel=next_is_vowel,
                onset_delay=onset_delay)
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
# PH SPEC v9
# Passes word_final flag into spec
# so trajectory builder and source
# builder can use it.
# ============================================================

def ph_spec_v9(ph, dur_ms,
                pitch=PITCH, oq=0.65,
                bw_mult=1.0, amp=1.0,
                next_ph=None,
                rest_ms=0.0,
                word_final=False,
                sr=SR):
    """
    v9 phoneme spec.
    Adds word_final flag for
    bypass onset and duration decisions.
    """
    spec = ph_spec_v7(
        ph, dur_ms,
        pitch=pitch, oq=oq,
        bw_mult=bw_mult, amp=amp,
        next_ph=next_ph,
        rest_ms=rest_ms,
        sr=sr)
    spec['word_final'] = word_final
    return spec


# ============================================================
# PHRASE SYNTHESIS v9
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    v9: All fixes active.
      FIX 1: DH voiced fraction 0.30.
      FIX 2: H = pure aspiration.
      FIX 3: Word-final sibilant cap 120ms.
      FIX 4: Bypass onset delayed by n_on//2.
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
    print("VOICE PHYSICS v9")
    print("Consonant identity fixes.")
    print()
    print("  FIX 1: DH voiced fraction 0.70→0.30")
    print("         DH max 75ms.")
    print("         Dental friction is identity.")
    print("         Voicing is secondary.")
    print()
    print("  FIX 2: H = pure aspiration")
    print("         Zero modal voicing during H.")
    print("         H max 75ms.")
    print("         Breathiness is identity.")
    print()
    print("  FIX 3: Word-final sibilant cap 120ms")
    print("         S/Z before rest: max 120ms.")
    print("         Sibilant ends. Rest begins.")
    print("         No trailing hiss.")
    print()
    print("  FIX 4: Bypass onset delay")
    print("         Bypass starts at n_on//2.")
    print("         Tract halfway to fricative")
    print("         before sibilance begins.")
    print("         No vowel+hiss smear.")
    print("="*60)
    print()

    # Calibrate gains
    print("  Calibrating gains...")
    recalibrate_gains_v8(sr=SR)
    print()

    # Primary diagnostic phrase
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

    # Targeted isolation tests
    # These test exactly the four reported problems.
    print()
    print("  Isolation tests...")

    # Test 1: "the" — should not have "ea" prefix
    seg = synth_phrase(
        [('the', ['DH', 'AH'])],
        pitch_base=PITCH)
    write_wav(
        "output_play/test_the.wav",
        apply_room(seg, rt60=1.2, dr=0.55))
    print("    test_the.wav")
    print("    → should be: clean 'the'")
    print("      NOT: 'ea-the'")

    # Test 2: "here" — no CH prefix
    seg = synth_phrase(
        [('here', ['H', 'IH', 'R'])],
        pitch_base=PITCH)
    write_wav(
        "output_play/test_here.wav",
        apply_room(seg, rt60=1.2, dr=0.55))
    print("    test_here.wav")
    print("    → should be: breathy 'here'")
    print("      NOT: 'CH-here'")

    # Test 3: "was" — Z ends cleanly
    seg = synth_phrase(
        [('was', ['W', 'AH', 'Z'])],
        pitch_base=PITCH)
    write_wav(
        "output_play/test_was.wav",
        apply_room(seg, rt60=1.2, dr=0.55))
    print("    test_was.wav")
    print("    → Z should end at the vowel boundary")
    print("      NOT: dragged out separately")

    # Test 4: "voice" — S ends cleanly
    seg = synth_phrase(
        [('voice', ['V', 'OY', 'S'])],
        pitch_base=PITCH)
    write_wav(
        "output_play/test_voice.wav",
        apply_room(seg, rt60=1.2, dr=0.55))
    print("    test_voice.wav")
    print("    → S should follow OY naturally")
    print("      NOT: announced or separated")

    # Full phrase variants
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
            f"output_play/the_voice_{label}.wav",
            apply_room(
                seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Additional phrases covering DH and H
    print()
    print("  DH and H phrase tests...")
    for label, words, punct in [
        ('this_is_here',
         [('this', ['DH', 'IH', 'S']),
          ('is',   ['IH', 'Z']),
          ('here', ['H',  'IH', 'R'])], '.'),
        ('that_was_always',
         [('that',   ['DH', 'AE', 'T']),
          ('was',    ['W',  'AH', 'Z']),
          ('always', ['AA', 'L',  'W',
                       'EH', 'Z'])], '.'),
        ('here_and_there',
         [('here',  ['H',  'IH', 'R']),
          ('and',   ['AE', 'N',  'D']),
          ('there', ['DH', 'EH', 'R'])], '.'),
        ('still_here',
         [('still', ['S', 'T', 'IH', 'L']),
          ('here',  ['H', 'IH', 'R'])], '.'),
        ('water_home',
         [('water', ['W', 'AA', 'T', 'ER']),
          ('home',  ['H', 'OW', 'M'])], '.'),
    ]:
        seg = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        write_wav(
            f"output_play/phrase_{label}.wav",
            apply_room(
                seg, rt60=1.6, dr=0.48))
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  START HERE:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  FOUR TARGETED TESTS:")
    print("  afplay output_play/test_the.wav")
    print("  afplay output_play/test_here.wav")
    print("  afplay output_play/test_was.wav")
    print("  afplay output_play/test_voice.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  test_the.wav:")
    print("    Starts immediately with dental.")
    print("    No vowel before the DH.")
    print()
    print("  test_here.wav:")
    print("    Breathy onset directly into IH.")
    print("    Like a whispered 'here'.")
    print("    No affricate prefix.")
    print()
    print("  test_was.wav:")
    print("    W→AH→Z as one continuous word.")
    print("    Z ends where the vowel ends.")
    print("    Not separately announced.")
    print()
    print("  test_voice.wav:")
    print("    V→OY→S as one continuous word.")
    print("    S follows OY naturally.")
    print("    Not announced as a separate event.")
    print()
