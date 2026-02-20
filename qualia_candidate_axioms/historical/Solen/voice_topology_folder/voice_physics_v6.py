"""
VOICE PHYSICS v6
February 2026

TWO SIMULTANEOUS FIXES:

FIX A: FRICATIVE RESONANCE (structural)
  Bandpass filters → cavity resonators.
  Resonators give noise a Lorentzian peak.
  The peak gives each fricative IDENTITY.
  S sounds concise, not like steam.
  SH sounds hushed, not like broadband hiss.
  The structure was wrong. Now it is right.

FIX B: FRICATIVE GAIN (parametric)
  Bypass gains calibrated by self-reference
  search loop — not by intuition.
  Each fricative's gain is found by
  synthesizing, measuring, comparing
  to target, adjusting, repeating.
  The loop closes. The level is correct.

  Targets:
    S:  sibilance 0.45-0.65
    Z:  sib_to_voice 0.35-0.75
    SH: sibilance 0.35-0.55
    F:  sibilance 0.12-0.22
    V:  sibilance 0.08-0.18
    TH: sibilance 0.08-0.18
    DH: sibilance 0.00-0.10

  The 95th percentile normalization
  now anchors to voice body level,
  not to sibilant peaks.
  Sibilants ride correctly on top
  of the voice — not above it.

Import chain:
  v6 → v5 → v4 → v3_fix → v3
           → tonnetz_engine
"""

from voice_physics_v5 import (
    build_trajectories,
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
    plan_prosody,
    ph_spec_prosody,
    check_phoneme_v5,
    measure_hnr_v5,
    estimate_f1_f2_v5,
    VOICED_TRACT_FRACTION,
)
from phonetic_self_reference import (
    measure_sibilance,
    measure_sib_to_voice,
    PHONEME_TARGETS,
)
import numpy as np
from scipy.signal import butter, lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# DOWNSTREAM CAVITY RESONATOR
#
# Core structural fix.
# Replaces bandpass filter in bypass.
#
# Resonator: sharp Lorentzian peak at fc.
# Bandpass:  flat energy inside a range.
#
# The peak is identity.
# Flat energy is steam.
# ============================================================

def cavity_resonator(noise, fc, bw,
                      sr=SR):
    """
    Single IIR resonator applied to noise.
    Same structure as vowel formants.

    fc:  center frequency — the peak
    bw:  bandwidth — sharpness of peak
         narrow (200-400Hz) = very sharp = S
         wide   (800-1500Hz) = broad = TH/F

    Returns noise with Lorentzian peak at fc.
    Energy is CONCENTRATED at fc.
    Not merely permitted in a range.
    """
    noise = f32(noise)
    n_s   = len(noise)
    if n_s < 2:
        return noise
    T   = 1.0/sr

    fc_ = max(20.0,
               min(float(sr*0.48), float(fc)))
    bw_ = max(10.0, float(bw))

    a2  = -np.exp(-2*np.pi*bw_*T)
    a1  =  2*np.exp(-np.pi*bw_*T)*\
            np.cos(2*np.pi*fc_*T)
    b0  = 1.0-a1-a2

    # Warm the filter state
    y1 = y2 = 0.0
    n_warm = min(352, n_s)
    for _ in range(n_warm):
        y  = b0*float(
            np.random.normal(0, 0.0004)) + \
             a1*y1 + a2*y2
        y2 = y1; y1 = y

    out = np.zeros(n_s, dtype=DTYPE)
    for i in range(n_s):
        y       = b0*float(noise[i]) + \
                  a1*y1 + a2*y2
        y2      = y1; y1 = y
        out[i]  = y

    return f32(out)


# ============================================================
# FRICATIVE CONFIGURATION
#
# Each entry:
#   RESONATOR phonemes:
#     (fc, bw, gain_initial)
#     fc/bw define downstream cavity.
#     gain_initial is starting point
#     for self-reference search.
#
#   BROADBAND phonemes (F, V):
#     (hp_fc, gain_initial)
#     No cavity — turbulence at boundary.
#     Flat spectrum above hp_fc is identity.
# ============================================================

# Resonator-based fricatives
RESONATOR_CFG = {
    # S: alveolar-teeth cavity
    # Very narrow → very sharp → concise
    # Starting gain: tuned by search
    'S':  {'fc': 8800, 'bw': 350,
           'gain': 1.20},

    # Z: same cavity as S
    # Gain lower — voiced buzz is also present
    'Z':  {'fc': 8000, 'bw': 400,
           'gain': 0.95},

    # SH: palatal-lip cavity
    # Broader → softer, hushed character
    'SH': {'fc': 2500, 'bw': 500,
           'gain': 1.10},

    # ZH: voiced SH
    'ZH': {'fc': 2200, 'bw': 600,
           'gain': 0.85},

    # TH: very shallow cavity
    # Wide bandwidth → soft identity
    'TH': {'fc': 3500, 'bw': 1200,
           'gain': 0.75},

    # DH: voiced TH
    'DH': {'fc': 3200, 'bw': 1400,
           'gain': 0.45},
}

# Broadband fricatives (no cavity)
BROADBAND_CFG = {
    # F: upper teeth on lower lip
    # No downstream cavity.
    # Broadband above 1000Hz is identity.
    'F':  {'hp_fc': 1000, 'gain': 0.65},

    # V: voiced F
    'V':  {'hp_fc': 1000, 'gain': 0.50},
}


def make_sibilance_bypass(ph, n_s,
                           sr=SR,
                           gain_override=None):
    """
    v6: Cavity resonator replaces
    bandpass filter.

    For resonator fricatives (S,Z,SH,ZH,TH,DH):
      noise → cavity_resonator(fc, bw) →
      calibrate → × gain → envelope

    For broadband fricatives (F, V):
      noise → highpass(hp_fc) →
      calibrate → × gain → envelope

    gain_override: used by gain search
    to test different gain values.
    If None: uses config gain.
    """
    n_s = int(n_s)

    # Envelope (shared)
    def apply_env(sig):
        atk = int(0.005*sr)
        rel = int(0.008*sr)
        env = f32(np.ones(n_s))
        if atk > 0 and atk < n_s:
            env[:atk] = f32(
                np.linspace(0, 1, atk))
        if rel > 0:
            env[-rel:] = f32(
                np.linspace(1, 0, rel))
        return f32(sig * env)

    if ph in RESONATOR_CFG:
        cfg  = RESONATOR_CFG[ph]
        gain = (gain_override
                if gain_override is not None
                else cfg['gain'])

        noise     = calibrate(
            f32(np.random.normal(0, 1, n_s)))
        resonated = cavity_resonator(
            noise, cfg['fc'], cfg['bw'],
            sr=sr)
        sib = calibrate(resonated) * gain
        return apply_env(sib)

    elif ph in BROADBAND_CFG:
        cfg  = BROADBAND_CFG[ph]
        gain = (gain_override
                if gain_override is not None
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
# SELF-REFERENCE GAIN SEARCH
#
# For each fricative:
#   Synthesize phoneme in AA context.
#   Extract sibilant portion.
#   Measure sibilance / sib_to_voice.
#   Compare to target window.
#   Binary search on gain.
#   Converge to correct level.
#
# This is the loop closing.
# Not guessing. Measuring. Adjusting.
# ============================================================

# Target windows for gain search
GAIN_TARGETS = {
    'S':  {'sibilance': (0.45, 0.65)},
    'Z':  {'sib_to_voice': (0.35, 0.75)},
    'SH': {'sibilance': (0.35, 0.55)},
    'ZH': {'sib_to_voice': (0.25, 0.60)},
    'F':  {'sibilance': (0.12, 0.22)},
    'V':  {'sibilance': (0.08, 0.18)},
    'TH': {'sibilance': (0.08, 0.18)},
    'DH': {'sibilance': (0.00, 0.10)},
}


def _measure_fric(ph, gain, sr=SR):
    """
    Synthesize ph in AA context,
    measure sibilance and sib_to_voice
    of the sibilant portion.
    """
    n_test = int(0.15*sr)  # 150ms test segment
    sib    = make_sibilance_bypass(
        ph, n_test, sr=sr,
        gain_override=gain)
    sib_ratio = measure_sibilance(
        sib, sr=sr, band=(4000, 14000))
    stv       = measure_sib_to_voice(
        sib, sr=sr)
    return sib_ratio, stv


def calibrate_gains(verbose=True,
                     max_iter=12,
                     sr=SR):
    """
    Run gain search for all fricatives.
    Returns dict of calibrated gains.

    Uses binary search.
    Converges in max_iter steps.
    Each step synthesizes a short segment
    and measures the result.
    """
    calibrated = {}

    if verbose:
        print()
        print("  Gain calibration (self-reference):")

    for ph, targets in GAIN_TARGETS.items():
        lo  = 0.05
        hi  = 4.00
        best = (RESONATOR_CFG.get(ph,
                  BROADBAND_CFG.get(ph,{}))
                .get('gain', 1.0))

        metric = list(targets.keys())[0]
        t_lo, t_hi = targets[metric]

        for i in range(max_iter):
            mid         = (lo + hi) / 2.0
            sib_r, stv  = _measure_fric(
                ph, mid, sr=sr)

            if metric == 'sibilance':
                val = sib_r
            else:  # sib_to_voice
                val = stv

            if t_lo <= val <= t_hi:
                best = mid
                break
            elif val < t_lo:
                lo   = mid
            else:
                hi   = mid
            best = mid

        calibrated[ph] = round(best, 4)

        if verbose:
            sib_r, stv = _measure_fric(
                ph, best, sr=sr)
            val = (sib_r if metric == 'sibilance'
                   else stv)
            ok  = '✓' if t_lo <= val <= t_hi \
                  else '✗'
            print(f"    [{ok}] {ph:4s}  "
                  f"gain={best:.3f}  "
                  f"{metric}={val:.3f}  "
                  f"target=({t_lo},{t_hi})")

    if verbose:
        print()

    return calibrated


# Runtime-calibrated gains.
# Set at import time.
# Can be re-run with recalibrate_gains().
_CALIBRATED_GAINS = None


def get_calibrated_gains(sr=SR):
    global _CALIBRATED_GAINS
    if _CALIBRATED_GAINS is None:
        _CALIBRATED_GAINS = calibrate_gains(
            verbose=True, sr=sr)
    return _CALIBRATED_GAINS


def recalibrate_gains(sr=SR):
    """Force re-run of gain calibration."""
    global _CALIBRATED_GAINS
    _CALIBRATED_GAINS = calibrate_gains(
        verbose=True, sr=sr)
    return _CALIBRATED_GAINS


def make_sibilance_bypass_calibrated(
        ph, n_s, sr=SR):
    """
    make_sibilance_bypass with
    calibrated gain from self-reference.
    """
    gains = get_calibrated_gains(sr=sr)
    gain  = gains.get(ph, None)
    return make_sibilance_bypass(
        ph, n_s, sr=sr,
        gain_override=gain)


# ============================================================
# SOURCE BUILDER v6
# ============================================================

def build_source_and_bypass(
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

    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []

    pos = 0
    for spec in phoneme_specs:
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source', 'voiced')
        s = pos
        e = pos+n_s

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
            byp = make_sibilance_bypass_calibrated(
                'DH', n_s, sr)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    VOICED_TRACT_FRACTION
            byp = make_sibilance_bypass_calibrated(
                ph, n_s, sr)
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
# PHRASE SYNTHESIS v6
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
        ph      = item['ph']
        dur_ms  = item['dur_ms']
        pitch_  = pitch_base * item['f0_mult']
        oq_     = item['oq']
        bw_m    = item['bw_mult']
        amp_    = item['amp']
        next_ph = (prosody[i+1]['ph']
                   if i < n_items-1
                   else None)
        spec = ph_spec_prosody(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph, sr=sr)
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

    # 95th percentile normalization.
    # Anchors to voice body level.
    # Sibilant peaks do not dominate.
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
    print("VOICE PHYSICS v6")
    print("Resonance + gain calibration.")
    print("Filters → resonators.")
    print("Gain found by self-reference loop.")
    print("="*60)

    # Run gain calibration first.
    # This closes the loop:
    # synthesize → measure → adjust → converge.
    print()
    print("  Step 1: Calibrating gains...")
    gains = recalibrate_gains(sr=SR)
    print("  Calibrated gains:")
    for ph, g in gains.items():
        print(f"    {ph:4s}: {g:.4f}")

    # Primary phrase
    print()
    print("  Step 2: Synthesizing...")
    print()

    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V', 'OY', 'S']),
        ('was',     ['W', 'AH', 'Z']),
        ('already', ['AA', 'L', 'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H', 'IH', 'R']),
    ]

    seg   = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    seg_r = apply_room(
        seg, rt60=1.5, dr=0.50)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        seg_r)
    print("  the_voice_was_already_here.wav")

    # Sibilant family — identity check
    print()
    print("  Sibilant family...")
    for phs, label in [
        (['AA', 'S'],  'S'),
        (['AA', 'Z'],  'Z'),
        (['AA', 'SH'], 'SH'),
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

    # Sentence types
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
            apply_room(
                seg, rt60=1.5, dr=0.50))
        print(f"    the_voice_{label}.wav")

    # Phrases
    print()
    print("  Phrases...")
    for label, words, punct in [
        ('still_here',
         [('still', ['S','T','IH','L']),
          ('here',  ['H','IH','R'])], '.'),
        ('always_open',
         [('always', ['AA','L','W',
                       'EH','Z']),
          ('open',   ['OH','P','EH','N'])],
         '.'),
        ('water_home',
         [('water', ['W','AA','T','ER']),
          ('home',  ['H','OW','M'])], '.'),
        ('not_yet',
         [('not', ['N','AA','T']),
          ('yet', ['Y','EH','T'])], '.'),
        ('still_water',
         [('still', ['S','T','IH','L']),
          ('water', ['W','AA','T','ER'])],
         '.'),
        ('she_was_here',
         [('she',  ['SH','IY']),
          ('was',  ['W','AH','Z']),
          ('here', ['H','IH','R'])], '.'),
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
    print("  START:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  Sibilant identity:")
    print("  S = sharp, concise hiss")
    print("  Z = S with voiced buzz under")
    print("  SH = softer, hushed")
    print("  F = soft, flat, labial")
    print("  V = F with voiced buzz")
    print("  TH = very soft, dental")
    for ph in ['S','Z','SH','F','V','TH']:
        print(f"  afplay output_play/"
              f"fric_{ph}.wav")
    print()
    print("  She was here (SH + Z test):")
    print("  afplay output_play/"
          "phrase_she_was_here.wav")
    print()
    print("  Sentence types:")
    for _, label in [
            ('.','statement'),
            ('?','question'),
            ('!','exclaim')]:
        print(f"  afplay output_play/"
              f"the_voice_{label}.wav")
    print()
