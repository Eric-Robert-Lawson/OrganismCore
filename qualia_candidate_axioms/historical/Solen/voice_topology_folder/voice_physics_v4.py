"""
VOICE PHYSICS v8
February 2026

THE SIBILANCE FIX.

Root cause discovered by self-reference:
  S sibilance = 0.009 (should be ≥ 0.65)
  Z sibilance = 0.000 (should be ≥ 0.40)

Both are near zero because:
  Sibilance (>6000Hz) was routed
  through a tract model with
  resonators only up to 3500Hz.
  The tract filtered out
  all sibilance content.

Fix:
  Fricative sibilance BYPASSES the tract.
  Added directly to post-tract output.
  The tract shapes the voiced component.
  The sibilance bypass carries
  the downstream cavity resonance.
  They are mixed at the output.
  They do not corrupt each other.

This matches the physics:
  Fricative noise source is at
  the front of the tract.
  It does not travel through
  the pharyngeal resonators.
  It radiates from the mouth
  shaped only by the small
  downstream cavity.

Self-reference targets:
  S: sibilance ≥ 0.65
  Z: sibilance ≥ 0.40, voiced=True
  Z: sib_to_voice ≥ 0.35
"""

from voice_physics_v3_fix import (
    plan_prosody,
    ph_spec_prosody,
    build_trajectories,
    breath_rest,
    VOWEL_F, GAINS,
    WORD_SYLLABLES,
    get_f, get_b, scalar,
    safe_bp, safe_lp, safe_hp,
    apply_room, write_wav,
    TARGET_RMS, calibrate, rms,
    PITCH, DIL, SR, DTYPE, f32,
)
from phonetic_self_reference import (
    check_phoneme,
    measure_sibilance,
    measure_sib_to_voice,
)
import numpy as np
from scipy.signal import butter, lfilter
import wave as wave_module
import os

os.makedirs("output_play", exist_ok=True)


def warm(fc, bw, n_warm=352, sr=SR):
    fc_ = max(20.0, min(
        float(sr*0.48), scalar(fc)))
    bw_ = max(10.0, scalar(bw))
    T   = 1.0/sr
    a2  = -np.exp(-2*np.pi*bw_*T)
    a1  =  2*np.exp(-np.pi*bw_*T)*\
            np.cos(2*np.pi*fc_*T)
    b0  = 1.0-a1-a2
    y1 = y2 = 0.0
    for _ in range(int(n_warm)):
        y  = b0*np.random.normal(
            0, 0.0004)+a1*y1+a2*y2
        y2=y1; y1=y
    return y1, y2

def resonator(x_arr, f_arr, b_arr,
               y1_in=0.0, y2_in=0.0,
               sr=SR):
    n_s = len(x_arr)
    T   = 1.0/sr
    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_in)
    y2  = float(y2_in)
    for i in range(n_s):
        fc  = max(20.0, min(
            float(sr*0.48),
            float(f_arr[i])))
        bw  = max(10.0, float(b_arr[i]))
        a2  = -np.exp(-2*np.pi*bw*T)
        a1  =  2*np.exp(-np.pi*bw*T)*\
                np.cos(2*np.pi*fc*T)
        b0  = 1.0-a1-a2
        y   = b0*float(x_arr[i])+\
              a1*y1+a2*y2
        y2=y1; y1=y
        out[i]=y
    return out, y1, y2

def tract(source, F_arrays, B_arrays,
           gains, states=None, sr=SR):
    n      = len(source)
    result = np.zeros(n, dtype=DTYPE)
    new_st = []
    for fi in range(4):
        if states is not None:
            y1 = float(states[fi][0])
            y2 = float(states[fi][1])
        else:
            f0_ = float(F_arrays[fi][0])
            b0_ = float(B_arrays[fi][0])
            y1,y2 = warm(f0_, b0_, sr=sr)
        out,y1,y2 = resonator(
            source, F_arrays[fi],
            B_arrays[fi],
            y1_in=y1, y2_in=y2, sr=sr)
        result += out*float(gains[fi])
        new_st.append((y1,y2))
    return result, new_st


# ============================================================
# SIBILANCE BYPASS GENERATOR
#
# The fix.
# Fricative sibilance generated
# separately from the tract.
# Added to post-tract output.
# The tract never sees it.
# The sibilance never gets filtered out.
# ============================================================

def make_sibilance_bypass(
        ph, n_s, sr=SR):
    """
    Generate the sibilance component
    that BYPASSES the tract.

    This is the downstream cavity shaping:
    a small resonance in front of
    the constriction.
    Not the pharyngeal tract.
    Not the formant bank.
    Just the mouth-front + teeth edge.

    Returns calibrated sibilance array
    ready to add to post-tract output.

    Gain levels derived from
    self-reference targets:
      S:  sibilance ≥ 0.65
      Z:  sibilance ≥ 0.40
      SH: sibilance ≥ 0.55
    """
    # Downstream cavity resonance
    # by place of articulation
    BYPASS_CFG = {
        # (d_res, d_bw, broadband_frac,
        #  cavity_frac, output_gain)
        #
        # S: alveolar + teeth edge
        # Small cavity → 8800Hz
        # Sharp, hissy
        'S':  (8800, 700,
               0.15, 0.85, 1.20),

        # Z: same as S
        # (sibilance same level as S)
        'Z':  (8000, 800,
               0.15, 0.85, 1.00),

        # SH: palatal + rounded lips
        # Larger cavity → 2500Hz
        # Softer, hushed
        'SH': (2500, 600,
               0.20, 0.80, 0.95),

        # ZH: same as SH
        'ZH': (2200, 700,
               0.20, 0.80, 0.80),

        # F: lip-tooth gap
        # No downstream cavity
        # Very soft broadband
        'F':  (None, None,
               1.00, 0.00, 0.45),

        # V: same as F (voiced F)
        'V':  (None, None,
               1.00, 0.00, 0.35),

        # TH: tongue-teeth
        # Slightly more defined than F
        'TH': (None, None,
               1.00, 0.00, 0.50),

        # DH: voiced TH
        'DH': (None, None,
               1.00, 0.00, 0.22),
    }

    cfg = BYPASS_CFG.get(ph)
    if cfg is None:
        return f32(np.zeros(n_s))

    d_res, d_bw, bb_f, cav_f, gain = cfg

    # Start with calibrated noise
    noise = calibrate(
        f32(np.random.normal(0,1,n_s)))

    # Broadband shaping
    # (the turbulent jet character)
    lo_freq = {
        'S': 4000,'Z': 4000,
        'SH':1000,'ZH':1000,
        'F': 200, 'V': 200,
        'TH':500, 'DH':500,
    }.get(ph, 1000)

    try:
        b,a = safe_bp(
            min(lo_freq, sr*0.47),
            min(14000,   sr*0.48),
            sr)
        broad = f32(lfilter(b,a,noise))
    except:
        broad = noise.copy()

    # Downstream cavity resonance
    if d_res is not None and \
       d_bw is not None:
        try:
            lo_ = max(100, d_res-d_bw//2)
            hi_ = min(sr*0.48,
                       d_res+d_bw//2)
            b,a  = safe_bp(lo_, hi_, sr)
            cav  = f32(lfilter(b,a,noise))
            sib  = broad*bb_f + cav*cav_f
        except:
            sib = broad
    else:
        sib = broad

    # Calibrate and apply gain
    sib = calibrate(sib) * gain

    # Envelope: brief onset/offset
    atk = int(0.005*sr)
    rel = int(0.008*sr)
    env = f32(np.ones(n_s))
    if atk > 0 and atk < n_s:
        env[:atk] = f32(
            np.linspace(0,1,atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1,0,rel))

    return f32(sib * env)


# ============================================================
# SOURCE BUILDER v8
# Voiced source through tract.
# Sibilance bypass generated separately.
# Mixed at output.
# ============================================================

def build_source_and_bypass(
        phoneme_specs, sr=SR):
    """
    Returns:
      voiced_source: goes through tract
      bypass_segs:   list of (pos, seg)
                     to add post-tract
    """
    n_total = sum(s['n_s']
                  for s in phoneme_specs)

    # F0 and oq trajectories
    f0_traj = np.zeros(n_total,
                        dtype=DTYPE)
    oq_traj = np.zeros(n_total,
                        dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s     = spec['n_s']
        f0_this = spec.get('pitch', PITCH)
        oq_this = spec.get('oq', 0.65)
        f0_next = (phoneme_specs[si+1]
                   .get('pitch', PITCH)
                   if si < len(
                       phoneme_specs)-1
                   else f0_this)
        oq_next = (phoneme_specs[si+1]
                   .get('oq', 0.65)
                   if si < len(
                       phoneme_specs)-1
                   else oq_this)
        f0_traj[pos:pos+n_s] = \
            np.linspace(f0_this, f0_next,
                         n_s)
        oq_traj[pos:pos+n_s] = \
            np.linspace(oq_this, oq_next,
                         n_s)
        pos += n_s

    # Generate voiced source
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
        raw_v[i] = ((p/oq_)*(2-p/oq_)
                    if p < oq_ else
                    1-(p-oq_)/(
                        1-oq_+1e-9))
    raw_v = f32(np.diff(
        raw_v, prepend=raw_v[0]))
    try:
        b,a  = safe_lp(20, sr)
        sh   = f32(np.random.normal(
            0,1,n_total))
        sh   = f32(lfilter(b,a,sh))
        sh   = f32(np.clip(
            1+0.030*sh, 0.4, 1.6))
        raw_v = raw_v*sh
    except:
        pass
    asp = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_total))
    raw_v = raw_v + asp
    voiced_full = calibrate(raw_v)
    noise_full  = calibrate(
        f32(np.random.normal(0,1,n_total)))

    # Build tract source and bypass list
    tract_source = np.zeros(
        n_total, dtype=DTYPE)
    bypass_segs  = []

    FRIC_PHONEMES = {
        'S','Z','SH','ZH','F','V','TH','DH'}

    pos = 0
    for spec in phoneme_specs:
        n_s   = spec['n_s']
        ph    = spec['ph']
        stype = spec.get('source','voiced')
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
            ne  = np.zeros(n_s,dtype=DTYPE)
            ve  = np.zeros(n_s,dtype=DTYPE)
            if cs>0: ne[:cs]=1.0
            if n_x>0:
                fo=f32(np.linspace(1,0,n_x))
                ne[cs:cs+n_x]=fo
                ve[cs:cs+n_x]=1.0-fo
            if cs+n_x<n_s: ve[cs+n_x:]=1.0
            tract_source[s:e]=(
                noise_full[s:e]*ne+
                voiced_full[s:e]*ve)

        elif stype == 'dh':
            # DH: voiced through tract
            # Very light bypass
            tract_source[s:e] = \
                voiced_full[s:e]
            byp = make_sibilance_bypass(
                'DH', n_s, sr)
            bypass_segs.append((s, byp))

        elif stype in (
                'fric_u', 'fric_v'):
            # KEY FIX:
            # Voiced fricatives:
            # voiced component → tract
            # sibilance → bypass only
            #
            # Unvoiced fricatives:
            # silence through tract
            # sibilance → bypass only

            is_voiced = (stype=='fric_v')

            if is_voiced:
                # Voiced component through tract
                # at reduced level
                tract_source[s:e] = \
                    voiced_full[s:e]*0.55

            # else: tract source stays zero
            # (silence during unvoiced fric)

            # Sibilance bypass
            byp = make_sibilance_bypass(
                ph, n_s, sr)
            bypass_segs.append((s, byp))

        elif stype in (
                'stop_unvoiced',
                'stop_voiced'):
            clos_n  = spec.get('clos_n',0)
            burst_n = spec.get('burst_n',0)
            vot_n   = spec.get('vot_n',0)
            bamp    = spec.get(
                'burst_amp', 0.28)
            bhp     = spec.get(
                'burst_hp', 2000)
            is_vcd  = (
                stype=='stop_voiced')

            if is_vcd and clos_n>0:
                tract_source[s:s+clos_n]=\
                    voiced_full[s:s+clos_n]\
                    *0.055

            if burst_n>0:
                bs=clos_n; be=bs+burst_n
                if be<=n_s:
                    burst=noise_full[
                        s+bs:s+be].copy()
                    try:
                        b,a=safe_hp(bhp,sr)
                        burst=f32(
                            lfilter(b,a,burst))
                    except:
                        pass
                    benv=f32(np.exp(
                        -np.arange(burst_n)/
                        burst_n*20))
                    tract_source[s+bs:s+be]=\
                        burst*benv*bamp

            vot_s=clos_n+burst_n
            vot_e=vot_s+vot_n
            if vot_n>0 and vot_e<=n_s:
                ne2=f32(np.linspace(
                    1,0,vot_n))
                ve2=1.0-ne2
                tract_source[
                    s+vot_s:s+vot_e]=(
                    noise_full[s+vot_s:
                                s+vot_e]*ne2+
                    voiced_full[s+vot_s:
                                 s+vot_e]*ve2)
            tr_s=vot_e
            if tr_s<n_s:
                tract_source[s+tr_s:e]=\
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
    v8: sibilance bypass.
    Tract shapes vowels and voicing.
    Bypass carries fricative sibilance.
    Mixed at output.
    Self-checked.
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
        pitch_  = pitch_base*item['f0_mult']
        oq_     = item['oq']
        bw_m    = item['bw_mult']
        amp_    = item['amp']
        next_ph = prosody[i+1]['ph'] \
                  if i < n_items-1 \
                  else None
        spec = ph_spec_prosody(
            ph, dur_ms,
            pitch=pitch_, oq=oq_,
            bw_mult=bw_m, amp=amp_,
            next_ph=next_ph, sr=sr)
        specs.append(spec)

    F_full, B_full, _ = \
        build_trajectories(specs, sr=sr)
    n_total = sum(s['n_s'] for s in specs)

    # Build source + bypass list
    tract_src, bypass_segs = \
        build_source_and_bypass(
            specs, sr=sr)

    # Run tract (vowels + voicing only)
    out, _ = tract(
        tract_src, F_full, B_full,
        GAINS, states=None, sr=sr)

    # Add sibilance bypass AFTER tract
    # The sibilance was never attenuated.
    # It goes directly to the output.
    for pos, byp in bypass_segs:
        e = min(pos+len(byp), n_total)
        n = e-pos
        out[pos:e] += byp[:n]

    # Nasal antiformants
    T = 1.0/sr
    NASAL_AF = {
        'M':(1000,300),
        'N':(1500,350),
        'NG':(2000,400),
    }
    pos = 0
    for spec in specs:
        ph  = spec['ph']
        n_s = spec['n_s']
        if ph in NASAL_AF:
            af,abw = NASAL_AF[ph]
            seg    = out[pos:pos+n_s].copy()
            anti   = np.zeros(n_s,
                dtype=DTYPE)
            y1=y2=0.0
            for i in range(n_s):
                a2=-np.exp(-2*np.pi*abw*T)
                a1=2*np.exp(-np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0=1.0-a1-a2
                y=b0*float(seg[i])+\
                  a1*y1+a2*y2
                y2=y1; y1=y; anti[i]=y
            out[pos:pos+n_s]=\
                seg-f32(anti)*0.50
            out[pos:pos+n_s]*=0.52
            hg=int(0.012*sr)
            if hg>0 and hg<n_s:
                out[pos+n_s-hg:pos+n_s]=0.0
        pos += n_s

    # Prosody amplitude
    amp_env = np.ones(n_total,dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    # Phrase envelope
    atk = int(0.025*sr)
    rel = int(0.055*sr)
    env = f32(np.ones(n_total))
    if atk>0 and atk<n_total:
        env[:atk]=f32(
            np.linspace(0,1,atk))
    if rel>0:
        env[-rel:]=f32(
            np.linspace(1,0,rel))
    out = out*f32(amp_env)*env

    # Rests
    segs_out = []
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s     = spec['n_s']
        segs_out.append(
            out[pos:pos+n_s].copy())
        rest_ms = item.get('rest_ms',0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(rest_ms,sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))

    # 95th percentile normalization
    p95 = np.percentile(
        np.abs(final), 95)
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
        sig = apply_room(
            sig,rt60=rt60,dr=dr,sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN — with self-check
# ============================================================

if __name__ == "__main__":

    print()
    print("VOICE PHYSICS v8")
    print("Sibilance bypass.")
    print("The tract shapes the voice.")
    print("The bypass carries the hiss.")
    print("They meet at the output.")
    print("="*60)
    print()

    PHRASE = [
        ('the',     ['DH','AH']),
        ('voice',   ['V','OY','S']),
        ('was',     ['W','AH','Z']),
        ('already', ['AA','L','R',
                      'EH','D','IY']),
        ('here',    ['H','IH','R']),
    ]

    # Synthesize
    print("  Primary phrase...")
    seg = synth_phrase(
        PHRASE, punctuation='.',
        pitch_base=PITCH)
    seg_r = apply_room(
        seg, rt60=1.5, dr=0.50)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        seg_r)
    print("    the_voice_was_already_here.wav")

    # Self-check S and Z
    print()
    print("  Self-check: S and Z")
    print()
    for word, phs, ph_check in [
        ('was',   ['W','AH','Z'], 'Z'),
        ('voice', ['V','OY','S'], 'S'),
    ]:
        seg_w = synth_phrase(
            [(word, phs)],
            pitch_base=PITCH)
        n = len(seg_w)
        # Check final third — sibilant
        sib_seg = seg_w[2*n//3:]
        check_phoneme(
            ph_check, sib_seg,
            verbose=True)
        print()
        write_wav(
            f"output_play/"
            f"selfcheck_{word}.wav",
            apply_room(seg_w,
                        rt60=1.3,dr=0.55))

    # Sentence types
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.','statement'),
            ('?','question'),
            ('!','exclaim')]:
        seg = synth_phrase(
            PHRASE, punctuation=punct,
            pitch_base=PITCH)
        seg_r = apply_room(
            seg,rt60=1.5,dr=0.50)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            seg_r)
        print(f"    the_voice_{label}.wav")

    # Other phrases
    print()
    print("  Phrases...")
    phrases = [
        ('still_here',
         [('still',['S','T','IH','L']),
          ('here', ['H','IH','R'])],'.'),
        ('always_open',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('open',  ['OH','P','EH','N'])],
         '.'),
        ('water_home',
         [('water',['W','AA','T','ER']),
          ('home', ['H','OW','M'])],'.'),
    ]
    for label,words,punct in phrases:
        seg = synth_phrase(
            words,punctuation=punct,
            pitch_base=PITCH)
        seg_r = apply_room(
            seg,rt60=1.6,dr=0.48)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            seg_r)
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  Primary:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  Self-check words:")
    print("  afplay output_play/"
          "selfcheck_was.wav")
    print("  afplay output_play/"
          "selfcheck_voice.wav")
    print()
    print("  If self-check shows:")
    print("  Z: sibilance ≥ 0.40 ✓")
    print("  S: sibilance ≥ 0.65 ✓")
    print("  The bypass is working.")
    print("  The hiss is present.")
    print("  The voice has its S and Z.")
    print()
