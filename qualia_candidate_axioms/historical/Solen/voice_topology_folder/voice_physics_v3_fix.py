"""
VOICE PHYSICS v3 — AMPLITUDE FIX
February 2026

FIXES:
  1. No per-phoneme normalization.
     Natural levels preserved.
  2. All sources calibrated to
     same RMS before use.
  3. Prosody scaling is the ONLY
     amplitude modulation.
  4. 95th percentile final normalization.
     Pops don't anchor the phrase.

Everything else identical to v3.
"""

from voice_physics_v3 import (
    VOWEL_F, GAINS,
    WORD_SYLLABLES, WORDS_FLAT,
    plan_prosody, ph_spec_prosody,
    build_trajectories,
    get_f, get_b, scalar,
    safe_bp, safe_lp, safe_hp,
    apply_room, write_wav,
    breath_rest,
    PITCH, DIL, SR, DTYPE, f32
)

from voice_physics_v2 import PHON_DUR

import numpy as np
from scipy.signal import butter, lfilter
import wave as wave_module
import os

os.makedirs("output_play", exist_ok=True)

TARGET_RMS = 0.08  # unified reference level

def rms(x):
    return float(np.sqrt(
        np.mean(np.asarray(x,
            dtype=np.float32)**2)
        + 1e-12))

def calibrate(x, target=TARGET_RMS):
    """Scale signal to target RMS."""
    x  = f32(x)
    r  = rms(x)
    if r > 1e-10:
        x = x * (target/r)
    return x


def source_steady_cal(n_s, sr=SR):
    """Noise source at calibrated RMS."""
    n = f32(np.random.normal(0,1,int(n_s)))
    return calibrate(n)


def source_voiced_cal(pitch_hz, n_s,
                       oq=0.65,
                       jitter=0.005,
                       shimmer=0.030,
                       sr=SR):
    """
    Voiced source at calibrated RMS.
    No per-call normalization.
    Natural level preserved.
    Calibrated to TARGET_RMS.
    """
    n_s = int(n_s)
    if n_s < 2:
        return f32(np.zeros(2))
    T   = 1.0/sr
    t   = np.arange(n_s, dtype=np.float32)/sr

    vib = f32(np.clip(
        (t-0.05)/0.05, 0, 1))
    ft  = pitch_hz*(
        1+0.007*vib*
        np.sin(2*np.pi*5.0*t))

    ph  = np.zeros(n_s, dtype=np.float32)
    p   = 0.0
    for i in range(n_s):
        p += float(ft[i])*(
            1+np.random.normal(
                0, jitter))/sr
        if p >= 1.0: p -= 1.0
        ph[i] = p

    oq_ = max(0.40, min(0.85, float(oq)))
    src = np.where(ph < oq_,
        (ph/oq_)*(2-ph/oq_),
        1-(ph-oq_)/(1-oq_+1e-9))
    src = f32(np.diff(
        src, prepend=src[0]))

    try:
        b,a = safe_lp(20, sr)
        sh  = f32(np.random.normal(0,1,n_s))
        sh  = f32(lfilter(b,a,sh))
    except:
        sh  = f32(np.ones(n_s))
    sh  = f32(np.clip(
        1+shimmer*sh, 0.4, 1.6))

    breath_amp = 0.015 + \
                 0.025*(oq_-0.55)/0.30
    asp = f32(np.random.normal(
        0, breath_amp, n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))

    raw = src*sh + asp
    # Calibrate to reference level
    return calibrate(raw)


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
    out = np.zeros(n_s, dtype=np.float32)
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
    result = np.zeros(n, dtype=np.float32)
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


def build_source_calibrated(
        phoneme_specs, sr=SR):
    """
    FIX: All sources calibrated to
    TARGET_RMS before use.
    No level mismatch between
    voiced and noise segments.
    No pops at source transitions.
    """
    n_total = sum(s['n_s']
                  for s in phoneme_specs)

    # Build F0 trajectory
    f0_traj = np.zeros(n_total,
                        dtype=np.float32)
    oq_traj = np.zeros(n_total,
                        dtype=np.float32)
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

    # Generate voiced source —
    # sample by sample with
    # time-varying F0 and oq
    T   = 1.0/sr
    raw_v = np.zeros(n_total,
                      dtype=np.float32)
    p   = 0.0
    for i in range(n_total):
        f0  = float(f0_traj[i])
        oq_ = max(0.40, min(0.85,
                              float(oq_traj[i])))
        p  += f0*(1+np.random.normal(
            0, 0.005))*T
        if p >= 1.0: p -= 1.0
        if p < oq_:
            raw_v[i] = (p/oq_)*(2-p/oq_)
        else:
            raw_v[i] = 1-(p-oq_)/(
                1-oq_+1e-9)

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

    # FIX: calibrate BOTH sources
    # to the same TARGET_RMS
    voiced_full = calibrate(raw_v)
    noise_raw   = f32(np.random.normal(
        0, 1, n_total))
    noise_full  = calibrate(noise_raw)

    # Now both live in the same
    # amplitude world.
    # Bursts, crossfades, transitions:
    # all at the same reference level.

    source = np.zeros(n_total,
                       dtype=np.float32)

    pos = 0
    for spec in phoneme_specs:
        n_s   = spec['n_s']
        stype = spec.get('source',
                          'voiced')
        s = pos
        e = pos+n_s

        if stype == 'voiced':
            source[s:e] = voiced_full[s:e]

        elif stype == 'h':
            n_h = int(n_s*0.12)
            n_x = min(int(0.018*sr),
                       n_h, n_s-n_h)
            cs  = max(0, n_h-n_x)
            ne  = np.zeros(n_s,
                            dtype=np.float32)
            ve  = np.zeros(n_s,
                            dtype=np.float32)
            if cs>0: ne[:cs]=1.0
            if n_x>0:
                fo=f32(np.linspace(1,0,n_x))
                ne[cs:cs+n_x]=fo
                ve[cs:cs+n_x]=1.0-fo
            if cs+n_x<n_s:
                ve[cs+n_x:]=1.0
            source[s:e]=(
                noise_full[s:e]*ne+
                voiced_full[s:e]*ve)

        elif stype == 'dh':
            source[s:e]=voiced_full[s:e]

        elif stype == 'fric_v':
            bands  = spec.get('bands',[])
            n_gain = spec.get('n_gain',0.5)
            fn     = calibrate(
                source_steady_cal(n_s, sr))
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    shaped = f32(
                        lfilter(b,a,fn))
                    fn = fn*0.3+shaped*0.7
                except:
                    pass
            fn = calibrate(fn)*n_gain
            source[s:e]=(
                voiced_full[s:e]*0.65+
                fn*0.35)

        elif stype == 'fric_u':
            bands  = spec.get('bands',[])
            d_res  = spec.get('d_res',None)
            d_bw   = spec.get('d_bw', None)
            n_gain = spec.get('n_gain',0.85)
            fn     = noise_full[s:e].copy()
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    fn=f32(lfilter(b,a,fn))
                except:
                    pass
            if d_res is not None \
               and d_bw is not None:
                try:
                    lo_=max(100,
                             d_res-d_bw//2)
                    hi_=min(sr*0.48,
                             d_res+d_bw//2)
                    b,a=safe_bp(lo_,hi_,sr)
                    sh2=f32(lfilter(b,a,fn))
                    fn=fn*0.15+sh2*0.85
                except:
                    pass
            fn = calibrate(fn)*n_gain
            source[s:e]=fn

        elif stype in ('stop_unvoiced',
                        'stop_voiced'):
            clos_n  = spec.get('clos_n',0)
            burst_n = spec.get('burst_n',0)
            vot_n   = spec.get('vot_n',0)
            # FIX: burst_amp now relative
            # to calibrated reference
            # not raw noise amplitude
            bamp    = spec.get(
                'burst_amp', 0.28)
            bhp     = spec.get(
                'burst_hp', 2000)
            is_vcd  = (stype=='stop_voiced')

            if is_vcd and clos_n>0:
                source[s:s+clos_n]=\
                    voiced_full[s:s+clos_n]\
                    *0.055

            if burst_n>0:
                bs=clos_n; be=bs+burst_n
                if be<=n_s:
                    # FIX: burst from
                    # calibrated noise
                    burst = noise_full[
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
                    # burst_amp is now
                    # relative to calibrated
                    # level — no explosion
                    source[s+bs:s+be]=\
                        burst*benv*bamp

            vot_s=clos_n+burst_n
            vot_e=vot_s+vot_n
            if vot_n>0 and vot_e<=n_s:
                ne2=f32(np.linspace(
                    1,0,vot_n))
                ve2=1.0-ne2
                source[s+vot_s:s+vot_e]=(
                    noise_full[s+vot_s:
                                s+vot_e]*ne2+
                    voiced_full[s+vot_s:
                                 s+vot_e]*ve2)
            tr_s=vot_e
            if tr_s<n_s:
                source[s+tr_s:e]=\
                    voiced_full[s+tr_s:e]

        pos += n_s

    return f32(source)


def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    Full phrase synthesis with
    calibrated amplitude.
    No per-phoneme normalization.
    One reference frame throughout.
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
        pitch_  = pitch_base * \
                  item['f0_mult']
        oq_     = item['oq']
        bw_m    = item['bw_mult']
        amp_    = item['amp']
        next_ph = prosody[i+1]['ph'] \
                  if i < n_items-1 \
                  else None
        spec = ph_spec_prosody(
            ph, dur_ms,
            pitch=pitch_,
            oq=oq_,
            bw_mult=bw_m,
            amp=amp_,
            next_ph=next_ph,
            sr=sr)
        specs.append(spec)

    F_full, B_full, _ = \
        build_trajectories(specs, sr=sr)

    n_total = sum(s['n_s'] for s in specs)

    # Calibrated source — no pops
    source = build_source_calibrated(
        specs, sr=sr)

    out, _ = tract(
        source, F_full, B_full,
        GAINS, states=None, sr=sr)

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
                dtype=np.float32)
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
                out[pos+n_s-hg:
                    pos+n_s]=0.0
        pos += n_s

    # Prosody amplitude — the ONLY
    # amplitude modulation
    amp_env = np.ones(n_total,
                       dtype=np.float32)
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

    out = out * f32(amp_env) * env

    # Insert breath rests
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

    # FIX: 95th percentile normalization.
    # One loud burst does not make
    # the whole phrase inaudible.
    p95 = np.percentile(
        np.abs(final), 95)
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
            sig,rt60=rt60,dr=dr,sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  "
          f"({dur:.2f}s)")


if __name__ == "__main__":

    os.makedirs("output_play",
                 exist_ok=True)

    print()
    print("VOICE PHYSICS v7 — AMPLITUDE FIX")
    print("One reference frame.")
    print("No per-phoneme normalization.")
    print("Calibrated sources.")
    print("95th percentile anchor.")
    print("="*60)
    print()

    # Primary diagnostic
    print("  Primary phrase...")
    seg = synth_phrase(
        [('the',  ['DH','AH']),
         ('voice',['V','OY','S']),
         ('was',  ['W','AH','Z']),
         ('already',['AA','L','R',
                      'EH','D','IY']),
         ('here', ['H','IH','R'])],
        punctuation='.',
        pitch_base=PITCH)
    seg = apply_room(seg,rt60=1.5,dr=0.50)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        seg)
    print("    the_voice_was_already_here.wav")

    # Punctuation comparison
    print()
    print("  Sentence types...")
    for punct, label in [
            ('.','statement'),
            ('?','question'),
            ('!','exclaim')]:
        seg = synth_phrase(
            [('the',  ['DH','AH']),
             ('voice',['V','OY','S']),
             ('was',  ['W','AH','Z']),
             ('already',['AA','L','R',
                          'EH','D','IY']),
             ('here', ['H','IH','R'])],
            punctuation=punct,
            pitch_base=PITCH)
        seg = apply_room(
            seg,rt60=1.5,dr=0.50)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            seg)
        print(f"    the_voice_{label}.wav")

    # Core phrases
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
        ('always_home',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('home',  ['H','OW','M'])],'.'),
    ]
    for label,words,punct in phrases:
        seg = synth_phrase(
            words,punctuation=punct,
            pitch_base=PITCH)
        seg = apply_room(
            seg,rt60=1.6,dr=0.48)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            seg)
        print(f"    phrase_{label}.wav")

    print()
    print("="*60)
    print()
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print("  'the' — audible now?")
    print("  D in 'already' — pop gone?")
    print("  H in 'here' — pop gone?")
    print("  S in 'voice' — proportionate?")
    print("  Overall level — consistent?")
    print()
