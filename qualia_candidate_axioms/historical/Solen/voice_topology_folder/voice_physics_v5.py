"""
VOICE PHYSICS v5
February 2026

FIXES FROM RAINBOW DIAGNOSTIC:

Rainbow scored 52%.
Analysis showed most failures were
measurement errors, not synthesis errors.
Real synthesis failures: sibilance too low.

FIX 1: SIBILANCE BYPASS GAINS ×3-8
  Rainbow showed:
    S:  sibilance=0.081 / target ≥0.65
    SH: sibilance=0.151 / target ≥0.55
    F:  sibilance=0.023 / target ≥0.20
    Z:  sibilance=0.218 / target ≥0.40
  All bypass gains raised substantially.

FIX 2: LPC PRE-EMPHASIS REDUCED
  Pre-emphasis coeff 0.97 → 0.50
  0.97 killed F1 in mid vowels.
  LPC reported F2 as F1.

FIX 3: HNR IN STEADY-STATE ZONE
  HNR was measured in onset/transition.
  Coarticulation looks like noise.
  Fix: measure final 25% of segment.

FIX 4: VOICED FRICATIVE TRACT MIX
  Voiced frac 0.55 → 0.75.
  Voice must be present above sibilance.

Import chain:
  v5 → v4 → v3_fix → v3 → v2
           → tonnetz_engine
"""

from voice_physics_v4 import (
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
)
from voice_physics_v3 import PHON_DUR_BASE
from phonetic_self_reference import (
    check_phoneme,
    measure_sibilance,
    measure_sib_to_voice,
    measure_hnr,
    PHONEME_TARGETS,
)
import numpy as np
from scipy.signal import butter, lfilter
import os

os.makedirs("output_play", exist_ok=True)


# ============================================================
# FIX 1: SIBILANCE BYPASS GAINS ×3-8
#
# All gains raised from rainbow targets.
# The downstream cavity resonance
# must dominate the fricative spectrum.
# ============================================================

BYPASS_CFG_V5 = {
    # S: alveolar + teeth edge → 8800Hz
    # gain: 1.20 → 3.50
    'S':  (8800, 700,  0.10, 0.90, 3.50),

    # Z: same cavity as S
    # gain: 1.00 → 2.80
    'Z':  (8000, 800,  0.10, 0.90, 2.80),

    # SH: palatal + rounded lips → 2500Hz
    # gain: 0.95 → 2.50
    'SH': (2500, 600,  0.15, 0.85, 2.50),

    # ZH: voiced SH
    # gain: 0.80 → 2.20
    'ZH': (2200, 700,  0.15, 0.85, 2.20),

    # F: lip-tooth, no cavity, broadband
    # gain: 0.45 → 1.50
    'F':  (None, None, 1.00, 0.00, 1.50),

    # V: voiced F
    # gain: 0.35 → 1.20
    'V':  (None, None, 1.00, 0.00, 1.20),

    # TH: tongue-teeth
    # gain: 0.50 → 1.60
    'TH': (None, None, 1.00, 0.00, 1.60),

    # DH: voiced TH
    # gain: 0.22 → 0.80
    'DH': (None, None, 1.00, 0.00, 0.80),
}


def make_sibilance_bypass(ph, n_s, sr=SR):
    """
    v5: Updated bypass gains.
    Physics identical to v4.
    Gains raised 3-8× from rainbow analysis.
    """
    cfg = BYPASS_CFG_V5.get(ph)
    if cfg is None:
        return f32(np.zeros(n_s))

    d_res, d_bw, bb_f, cav_f, gain = cfg

    noise = calibrate(
        f32(np.random.normal(0, 1, n_s)))

    lo_freq = {
        'S': 4000, 'Z': 4000,
        'SH': 1000, 'ZH': 1000,
        'F': 200,   'V': 200,
        'TH': 500,  'DH': 500,
    }.get(ph, 1000)

    try:
        b, a = safe_bp(
            min(lo_freq, sr*0.47),
            min(14000,   sr*0.48), sr)
        broad = f32(lfilter(b, a, noise))
    except:
        broad = noise.copy()

    if d_res is not None and \
       d_bw  is not None:
        try:
            lo_ = max(100, d_res - d_bw//2)
            hi_ = min(sr*0.48,
                       d_res + d_bw//2)
            b, a = safe_bp(lo_, hi_, sr)
            cav  = f32(lfilter(b, a, noise))
            sib  = broad*bb_f + cav*cav_f
        except:
            sib = broad
    else:
        sib = broad

    sib = calibrate(sib) * gain

    atk = int(0.005*sr)
    rel = int(0.008*sr)
    env = f32(np.ones(n_s))
    if atk > 0 and atk < n_s:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1, 0, rel))

    return f32(sib * env)


# ============================================================
# FIX 4: VOICED FRICATIVE TRACT MIX
# Raised from 0.55 → 0.75
# Voice must be clearly present.
# Sibilance rides on top of it.
# ============================================================

VOICED_TRACT_FRACTION = 0.75


def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    v5 source builder.
    FIX 1: uses v5 make_sibilance_bypass
    FIX 4: voiced fric tract = 0.75
    All other logic identical to v4.
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

    tract_source = np.zeros(n_total,
                             dtype=DTYPE)
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
            byp = make_sibilance_bypass(
                'DH', n_s, sr)
            bypass_segs.append((s, byp))

        elif stype in ('fric_u', 'fric_v'):
            if stype == 'fric_v':
                # FIX 4: 0.55 → 0.75
                tract_source[s:e] = \
                    voiced_full[s:e] * \
                    VOICED_TRACT_FRACTION
            # else: silence through tract

            # All sibilance via bypass
            byp = make_sibilance_bypass(
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
# PHRASE SYNTHESIS v5
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

    # Add sibilance bypass after tract
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
            anti    = np.zeros(n_s,
                dtype=DTYPE)
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
                out[pos+n_s-hg:pos+n_s] = 0.0
        pos += n_s

    # Prosody amplitude
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

    # Breath rests
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
# FIX 2+3: CORRECTED ANALYSIS TOOLS
# ============================================================

def estimate_f1_f2_v5(seg, sr=SR):
    """
    FIX 2: Pre-emphasis 0.97 → 0.50.
    0.97 attenuated F1 below ~700Hz.
    Mid vowels reported F2 as F1.
    0.50 is mild — all F1s findable.
    """
    from scipy.signal import find_peaks
    seg = f32(seg)
    n   = len(seg)
    if n < 128:
        return [0.0, 0.0, 0.0, 0.0]

    PRE_EMPH = 0.50
    pre = np.append(
        seg[0],
        seg[1:] - PRE_EMPH*seg[:-1])

    order = int(2 + sr/1000)
    order = min(order, n//3, 40)

    try:
        R = np.array([
            float(np.dot(
                pre[:n-k], pre[k:]))
            for k in range(order+1)])
        if abs(R[0]) < 1e-10:
            return [0.0, 0.0, 0.0, 0.0]

        a   = np.zeros(order)
        err = R[0]
        for i in range(order):
            k = R[i+1]
            for j in range(i):
                k -= a[j]*R[i-j]
            k    /= (err + 1e-10)
            a_new = a[:i] - k*a[:i][::-1]
            a[:i] = a_new
            a[i]  = k
            err  *= (1-k**2)

        n_fft = 1024
        H     = np.fft.rfft(
            np.append([1.0], -a), n=n_fft)
        spec  = 1.0/(np.abs(H)**2 + 1e-10)
        freqs = np.fft.rfftfreq(
            n_fft, d=1.0/sr)

        mask  = (freqs > 80) & \
                (freqs < 5000)
        s_m   = spec[mask]
        f_m   = freqs[mask]

        peaks, _ = find_peaks(
            s_m,
            height=np.max(s_m)*0.08,
            distance=int(80/(
                freqs[1]-freqs[0])+1))

        formants = sorted(
            [float(f_m[p]) for p in peaks])
        while len(formants) < 4:
            formants.append(0.0)
        return formants[:4]

    except:
        return [0.0, 0.0, 0.0, 0.0]


def measure_hnr_v5(seg, pitch_hz=175,
                    sr=SR):
    """
    FIX 3: HNR in steady-state zone.
    Measure final 25% of segment.
    Onset is coarticulation = looks noisy.
    Settled tail is where voiced
    character is clear.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 64:
        return 0.0

    # Final 25% — settled, not transitioning
    start = int(n*0.75)
    seg   = seg[start:]
    n     = len(seg)
    if n < 32:
        return 0.0

    T0 = int(sr / max(pitch_hz, 50))
    if T0 >= n:
        return 0.0

    r0 = float(np.sum(seg**2))
    r1 = float(np.sum(
        seg[:n-T0] * seg[T0:]))

    if r0 < 1e-12:
        return 0.0

    ratio = r1/r0
    ratio = max(-0.999, min(0.999, ratio))
    if ratio <= 0:
        return 0.0

    return float(10*np.log10(
        ratio/(1-ratio+1e-10)))


def check_phoneme_v5(ph, seg, sr=SR,
                      verbose=True):
    """
    v5 self-check.
    FIX 2: corrected LPC formant estimator.
    FIX 3: HNR in steady-state zone.
    Skips formant checks for phonemes
    requiring boundary-aware extraction.
    """
    target = PHONEME_TARGETS.get(ph)
    if target is None:
        return {}, True

    seg     = f32(seg)
    results = {}
    passed  = []
    failed  = []

    # FIX 3: steady-state HNR
    hnr    = measure_hnr_v5(
        seg, pitch_hz=PITCH, sr=sr)
    voiced = hnr > 3.0

    if 'voiced' in target:
        tgt_v = target['voiced']
        ok    = (voiced == tgt_v)
        results['voiced'] = {
            'target':   tgt_v,
            'measured': voiced,
            'hnr_db':   round(hnr, 1),
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'voiced')

    # Sibilance
    band = target.get(
        'sibilance_band', (6000, 12000))
    if 'sibilance_min' in target or \
       'sibilance_max' in target:
        sib   = measure_sibilance(
            seg, sr=sr, band=band)
        s_min = target.get(
            'sibilance_min', 0.0)
        s_max = target.get(
            'sibilance_max', 1.0)
        ok    = (s_min <= sib <= s_max)
        results['sibilance'] = {
            'target':   (s_min, s_max),
            'measured': round(sib, 3),
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'sibilance')

    # Sibilance-to-voice
    if 'sib_to_voice_min' in target:
        stv   = measure_sib_to_voice(
            seg, sr=sr)
        s_min = target['sib_to_voice_min']
        ok    = stv >= s_min
        results['sib_to_voice'] = {
            'target_min': s_min,
            'measured':   round(stv, 3),
            'pass':       ok,
        }
        (passed if ok else failed).append(
            'sib_to_voice')

    # HNR bounds
    if 'hnr_min' in target or \
       'hnr_max' in target:
        h_min = target.get('hnr_min', -99)
        h_max = target.get('hnr_max',  99)
        ok    = (h_min <= hnr <= h_max)
        results['hnr'] = {
            'target':   (h_min, h_max),
            'measured': round(hnr, 1),
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'hnr')

    # FIX 2: formants with corrected LPC
    # Only on phonemes where isolated
    # segment gives reliable reading.
    FORMANT_RELIABLE = {
        'AA','AE','AH','AO','AW','AY',
        'EH','ER','IH','IY','OH','OW',
        'OY','UH','UW',
    }
    if ph in FORMANT_RELIABLE and \
       any(k in target
           for k in ('f1','f2','f3')):
        fmts = estimate_f1_f2_v5(
            seg, sr=sr)
        for fi, fname in enumerate(
                ('f1','f2','f3','f4')):
            if fname in target:
                lo, hi   = target[fname]
                measured = fmts[fi]
                ok = (lo <= measured <= hi)
                results[fname] = {
                    'target':   (lo, hi),
                    'measured': round(
                        measured, 1),
                    'pass':     ok,
                }
                (passed if ok
                 else failed).append(fname)

    all_pass = len(failed) == 0

    if verbose:
        status = '✓' if all_pass else '✗'
        print(f"  [{status}] {ph}")
        for k, v in results.items():
            p = '  ✓' if v['pass'] \
                else '  ✗'
            print(
                f"    {p} {k}: "
                f"measured="
                f"{v.get('measured','?')}"
                f"  target="
                f"{v.get('target','')}")

    return results, all_pass


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v5")
    print("Rainbow diagnostic fixes applied.")
    print()
    print("  FIX 1: Bypass gains ×3-8")
    print("  FIX 2: LPC pre-emph 0.97→0.50")
    print("  FIX 3: HNR in steady-state")
    print("  FIX 4: Voiced fric tract 0.55→0.75")
    print("="*60)
    print()

    PHRASE = [
        ('the',     ['DH', 'AH']),
        ('voice',   ['V', 'OY', 'S']),
        ('was',     ['W', 'AH', 'Z']),
        ('already', ['AA', 'L', 'R',
                      'EH', 'D', 'IY']),
        ('here',    ['H', 'IH', 'R']),
    ]

    # Primary phrase
    print("  Primary phrase...")
    seg   = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    seg_r = apply_room(
        seg, rt60=1.5, dr=0.50)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        seg_r)
    print("    the_voice_was_already_here.wav")

    # Self-check S and Z with v5 tools
    print()
    print("  Self-check v5: sibilants")
    print()
    for word, phs, ph_check in [
        ('was',   ['W', 'AH', 'Z'], 'Z'),
        ('voice', ['V', 'OY', 'S'], 'S'),
    ]:
        seg_w   = synth_phrase(
            [(word, phs)],
            pitch_base=PITCH)
        n       = len(seg_w)
        sib_seg = seg_w[2*n//3:]
        check_phoneme_v5(
            ph_check, sib_seg,
            verbose=True)
        print()
        write_wav(
            f"output_play/"
            f"selfcheck_{word}.wav",
            apply_room(
                seg_w, rt60=1.3, dr=0.55))

    # Sentence types
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg   = synth_phrase(
            PHRASE, punctuation=punct,
            pitch_base=PITCH)
        seg_r = apply_room(
            seg, rt60=1.5, dr=0.50)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            seg_r)
        print(f"    the_voice_{label}.wav")

    # Additional phrases
    print()
    print("  Phrases...")
    phrases = [
        ('still_here',
         [('still', ['S','T','IH','L']),
          ('here',  ['H','IH','R'])],
         '.'),
        ('always_open',
         [('always', ['AA','L','W',
                       'EH','Z']),
          ('open',   ['OH','P','EH','N'])],
         '.'),
        ('water_home',
         [('water', ['W','AA','T','ER']),
          ('home',  ['H','OW','M'])],
         '.'),
        ('not_yet',
         [('not', ['N','AA','T']),
          ('yet', ['Y','EH','T'])],
         '.'),
        ('still_water',
         [('still', ['S','T','IH','L']),
          ('water', ['W','AA','T','ER'])],
         '.'),
    ]
    for label, words, punct in phrases:
        seg   = synth_phrase(
            words, punctuation=punct,
            pitch_base=PITCH)
        seg_r = apply_room(
            seg, rt60=1.6, dr=0.48)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            seg_r)
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  Sentence types:")
    for _, label in [
            ('.','statement'),
            ('?','question'),
            ('!','exclaim')]:
        print(f"  afplay output_play/"
              f"the_voice_{label}.wav")
    print()
    print("  SELF-CHECK TARGETS v5:")
    print("  S: sibilance ≥ 0.65")
    print("  Z: sibilance ≥ 0.40, voiced=True")
    print("  If passing: re-run rainbow.")
    print("  Expected score: >80%")
    print()
